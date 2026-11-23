#!/usr/bin/env python3
"""List and run ResearchClawEval benchmarks with the user's model provider."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parent.parent
PROVIDER_KEYS = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")
COMMON_OUTPUTS = ("research_idea.json", "experiment_trace.json", "final_report.md")
SLUG = re.compile(r"[a-z0-9][a-z0-9_-]*\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
PSYDEF_SHA256 = "88d55e1ae6f4653661baa795166ef103f5439f4d6720b1767c3be7bbc3904ad7"


@dataclass(frozen=True)
class Topic:
    id: str
    label: str
    dataset_dir: str
    visible_dir: str | None
    outputs: tuple[str, ...]

    @property
    def contract(self) -> Path:
        return ROOT / "contracts" / f"{self.id}_contract.md"


TOPICS = {topic.id: topic for topic in (
    Topic("babylm", "BabyLM-10M", "babylm", None, ()),
    Topic("mountaincar_continuous", "MountainCar-Continuous", "mountaincar_continuous", "src", ("config.yaml", "src", "checkpoints")),
    Topic("arc_wbe_2026", "ARC-WBE-2026", "arc_white_box_estimation_2026", "visible-validation", ("estimator.py",)),
    Topic("psydefdetect", "PsyDefDetect", "psydefdetect", None, ("predictions.jsonl",)),
    Topic("tdc_admet_tox", "TDC-ADMET-Tox", "tdc_admet_tox", "public", ("predictions.csv",)),
)}


class ArenaError(Exception):
    """An expected error with a short message suitable for the CLI."""


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ArenaError(f"Cannot read JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArenaError(f"Expected a JSON object in {path}")
    return value


def write_json(path: Path, value: object) -> None:
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def is_slug(value: object) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value)) and value != "all"


def load_adapter(directory: Path, *, builtin: bool) -> dict:
    directory = directory.resolve()
    adapter = read_json(directory / "adapter.json")
    name, identifier = adapter.get("name"), adapter.get("id")
    if not is_slug(identifier) or not isinstance(name, str) or not name.strip():
        raise ArenaError(f"{directory}: adapter needs a nonempty name and an ID other than 'all'")
    if builtin and directory.name != identifier:
        raise ArenaError(f"{directory}: built-in adapter ID must match its directory")
    topics = adapter.get("topics")
    if not isinstance(topics, dict) or not topics or set(topics) - TOPICS.keys():
        raise ArenaError(f"{directory}: topics must list known benchmark IDs")
    for topic, route in topics.items():
        if not isinstance(route, dict):
            raise ArenaError(f"{identifier}/{topic}: route must be a JSON object")
        if "reason" in route:
            if not isinstance(route["reason"], str) or not route["reason"].strip() or "command" in route:
                raise ArenaError(f"{identifier}/{topic}: unsupported route needs a reason and no command")
            continue
        command = route.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(x, str) or not x or "\0" in x for x in command):
            raise ArenaError(f"{identifier}/{topic}: command must be a nonempty argument array")
        image = route.get("image")
        if not isinstance(image, str) or not image or image.startswith("-") or any(c.isspace() for c in image):
            raise ArenaError(f"{identifier}/{topic}: invalid Docker image")
        marker = route.get("native_marker")
        if not isinstance(marker, str) or not marker.strip() or "\n" in marker:
            raise ArenaError(f"{identifier}/{topic}: specify a native log marker")
        if route.get("status", "experimental") not in {"experimental", "verified"}:
            raise ArenaError(f"{identifier}/{topic}: unknown runtime verification status")
        if "gpu" in route and not isinstance(route["gpu"], bool):
            raise ArenaError(f"{identifier}/{topic}: gpu must be a boolean")
        if "dockerfile" in route:
            dockerfile = route["dockerfile"]
            if not builtin or not isinstance(dockerfile, str):
                raise ArenaError(f"{identifier}/{topic}: custom adapters use an existing Docker image")
            recipe = (directory / dockerfile).resolve()
            if not recipe.is_relative_to(directory) or not recipe.is_file():
                raise ArenaError(f"{identifier}/{topic}: Dockerfile must be inside the adapter directory")
            url, commit = adapter.get("upstream_url"), adapter.get("upstream_commit")
            if not isinstance(url, str) or not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+\.git", url):
                raise ArenaError(f"{identifier}: an HTTPS GitHub clone URL is required")
            if not isinstance(commit, str) or not SHA.fullmatch(commit):
                raise ArenaError(f"{identifier}: an upstream commit SHA is required")
    return dict(adapter, directory=directory)


def load_builtins() -> dict[str, dict]:
    adapters = (load_adapter(path.parent, builtin=True) for path in sorted((ROOT / "adapters").glob("*/adapter.json")))
    return {adapter["id"]: adapter for adapter in adapters}


def get_route(adapter: dict, topic: Topic) -> dict:
    return adapter["topics"].get(topic.id, {"reason": "The adapter does not declare this task"})


def describe_pair(topic: Topic, adapter: dict, route: dict) -> dict:
    return {
        "topic": topic.id,
        "framework": adapter["id"],
        "status": "unsupported" if "reason" in route else route.get("status", "experimental"),
        **({"reason": route["reason"]} if "reason" in route else {"image": route["image"], "gpu": route.get("gpu", False)}),
    }


def provider_env(env_file: Path | None) -> dict[str, str]:
    values = {}
    if env_file is not None:
        for number, line in enumerate(env_file.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.removeprefix("export ").partition("=")
            if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key.strip()):
                raise ArenaError(f"Invalid key/value assignment in {env_file} at line {number}")
            key, value = key.strip(), value.strip()
            if key not in PROVIDER_KEYS:
                continue
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            values[key] = value
    for key in PROVIDER_KEYS:
        if key in os.environ:
            values[key] = os.environ[key]
    missing = [key for key in PROVIDER_KEYS if not values.get(key, "").strip()]
    if missing:
        raise ArenaError("Configure the model API before running. Missing: " + ", ".join(missing))
    url = urlsplit(values["OPENAI_BASE_URL"])
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ArenaError("OPENAI_BASE_URL must be an HTTP(S) URL without embedded credentials")
    if any(any(c in val for c in "\r\n\0") for val in values.values()):
        raise ArenaError("Model configuration must be single-line text")
    return values


def tool_env() -> dict:
    env = os.environ.copy()
    for key in (*PROVIDER_KEYS, "ARENA_ARC_SCORER_CONTAINER"):
        env.pop(key, None)
    return env


def check_call(command: list[str], label: str, *, timeout: int | None = None, quiet: bool = False) -> None:
    try:
        process = subprocess.run(command, cwd=ROOT, env=tool_env(), check=False, timeout=timeout,
                                 stdout=subprocess.DEVNULL if quiet else sys.stderr)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ArenaError(f"{label}: {exc}") from exc
    if process.returncode != 0:
        raise ArenaError(f"{label} failed (exit {process.returncode})")


def checkout_framework(adapter: dict, cache: Path) -> Path:
    revision = adapter["upstream_commit"]
    destination = cache / "sources" / f"{adapter['id']}-{revision}"
    if (destination / ".git").is_dir():
        try:
            head = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True, env=tool_env()).strip()
            tracked = subprocess.check_output(["git", "-C", str(destination), "status", "--porcelain", "--untracked-files=all"], text=True, env=tool_env())
        except subprocess.CalledProcessError as exc:
            raise ArenaError("Could not verify cached framework checkout") from exc
        if head != revision or tracked.strip():
            raise ArenaError(f"Cached framework checkout is not clean at the pinned revision: {destination}")
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="clone-", dir=destination.parent) as tmp:
        checkout = Path(tmp) / "source"
        check_call(["git", "init", "-q", str(checkout)], "Initialize upstream checkout")
        git = ["git", "-C", str(checkout)]
        check_call(git + ["fetch", "--depth", "1", adapter["upstream_url"], revision], "Fetch pinned framework version", timeout=600)
        check_call(git + ["checkout", "--detach", revision], "Check out pinned framework version")
        checkout.rename(destination)
    return destination


def prepare_image(adapter: dict, route: dict, cache: Path) -> str:
    if "dockerfile" not in route:
        return route["image"]
    recipe = adapter["directory"] / route["dockerfile"]
    signature = hashlib.sha256(recipe.read_bytes() + adapter["upstream_commit"].encode()).hexdigest()[:16]
    tag = f"rceval-arena/{adapter['id']}:{signature}"
    with (cache / ".build.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        found = subprocess.run(["docker", "image", "inspect", tag], env=tool_env(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if found.returncode != 0:
            checkout = checkout_framework(adapter, cache)
            check_call(["docker", "build", "--file", str(recipe), "--tag", tag, str(checkout)],
                       f"Build runtime for {adapter['id']}", timeout=3600)
    return tag


def prepare_dataset(topic: Topic, data_dir: Path) -> Path:
    with (data_dir / f".{topic.id}.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        check_call(["bash", str(ROOT / "scripts/setup_datasets.sh"), "--dataset", topic.id,
                    "--dir", str(data_dir)], f"Prepare {topic.label}", timeout=1800)
    dataset = (data_dir / topic.dataset_dir).resolve()
    visible = dataset / topic.visible_dir if topic.visible_dir else dataset
    if not visible.is_dir() or not any(visible.iterdir()):
        raise ArenaError(f"Dataset preparation did not produce the required public input: {visible}")
    return dataset


def project_visible_dataset(topic: Topic, dataset: Path, run: Path) -> Path:
    if topic.id != "psydefdetect":
        return dataset / topic.visible_dir if topic.visible_dir else dataset
    source = dataset / "PsyDefConv.json"
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != PSYDEF_SHA256:
        raise ArenaError("PsyDefDetect corpus does not match the published checksum")
    split_file = ROOT / "psydefdetect_split.canonical.json"
    split = read_json(split_file)
    eval_ids = set(split["eval_record_ids"])
    train_ids = set(split["train_record_ids"])
    rows = json.loads(data)
    visible = run / "visible"
    visible.mkdir()
    records = []
    for row in rows:
        if row["id"] in eval_ids:
            records.append({key: row[key] for key in ("id", "dialogue_id", "dialogue", "current_text")})
        elif row["id"] in train_ids:
            records.append(row)
    if len(records) != len(train_ids) + len(eval_ids):
        raise ArenaError("PsyDefDetect public corpus does not match the frozen split")
    (visible / "PsyDefConv.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    shutil.copyfile(split_file, visible / split_file.name)
    return visible


def mount(source: Path, target: str, *, readonly: bool) -> str:
    resolved = str(source.resolve())
    if any(c in resolved for c in ',"\n\r'):
        raise ArenaError("Docker input and output paths cannot contain commas, quotes or newlines")
    mode = ",readonly" if readonly else ""
    return f"type=bind,source={resolved},target={target}{mode}"


def docker_command(name: str, route: dict, image: str, adapter: Path, workspace: Path,
                   inputs: Path, dataset: Path) -> list[str]:
    command = ["docker", "run", "--rm", "--name", name, "--init", "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges", "--workdir", "/workspace",
               "--mount", mount(workspace, "/workspace", readonly=False),
               "--mount", mount(inputs, "/input", readonly=True),
               "--mount", mount(dataset, "/dataset", readonly=True),
               "--mount", mount(adapter, "/arena-adapter", readonly=True),
               "--mount", mount(ROOT / "scoring", "/arena-scoring", readonly=True),
               "--env", "WORKSPACE=/workspace", "--env", "DATASET_ROOT=/dataset",
               "--env", "ARENA_PROMPT=/input/prompt.txt", "--env", "ARENA_TOPIC",
               "--env", "HOME=/workspace/.home", "--env", "PYTHONUNBUFFERED=1"]
    for key in PROVIDER_KEYS:
        command.extend(("--env", key))
    if route.get("gpu"):
        command.extend(("--gpus", "all"))
    # An explicit argv keeps an image's default entrypoint out of the launch contract.
    return command + ["--entrypoint", route["command"][0], image, *route["command"][1:]]


def launch(command: list[str], name: str, topic: Topic, run: Path, provider: dict,
           timeout: int) -> str:
    logfile = run / "logs/e2e.log"
    # A private temporary log avoids writing unfiltered provider credentials to artifacts.
    with tempfile.TemporaryFile() as raw:
        try:
            completed = subprocess.run(command, env={**tool_env(), **provider, "ARENA_TOPIC": topic.id},
                                       cwd=ROOT, stdout=raw, stderr=subprocess.STDOUT, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            subprocess.run(["docker", "rm", "-f", name], env=tool_env(), timeout=30,
                           check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            raise
        finally:
            raw.seek(0)
            with logfile.open("wb") as output:
                for line in raw:
                    line = line.replace(provider["OPENAI_API_KEY"].encode(), b"[redacted]")
                    output.write(line)
    if completed.returncode:
        raise ArenaError(f"Native command exited with {completed.returncode}; see {logfile}")
    return logfile.read_text(encoding="utf-8", errors="replace")


def require_artifacts(topic: Topic, workspace: Path) -> dict:
    for name in COMMON_OUTPUTS + topic.outputs:
        path = workspace / name
        if not path.exists() or path.is_symlink():
            raise ArenaError(f"Native run is missing required regular output: {name}")
        if name in COMMON_OUTPUTS and (not path.is_file() or not path.stat().st_size):
            raise ArenaError(f"Expected a nonempty run artifact: {name}")
    trace = read_json(workspace / "experiment_trace.json")
    if trace.get("framework_native_execution") is not True or trace.get("consumed_topic_input") is not True:
        raise ArenaError("Trace must record native execution and use of the task input")
    if topic.id == "mountaincar_continuous" and len(list((workspace / "checkpoints").glob("config*.pkl"))) != 5:
        raise ArenaError("MountainCar requires exactly five config*.pkl checkpoints")
    return trace


def score_local(topic: Topic, workspace: Path, dataset: Path, run: Path) -> str | None:
    python = sys.executable
    output = run / "local_metrics.json"
    if topic.id == "psydefdetect":
        command = [python, "scoring/run_psydefdetect_local_score.py", "--dataset-root", str(dataset),
                   "--predictions", str(workspace / "predictions.jsonl"), "--output-score", str(output)]
    elif topic.id == "babylm":
        command = [python, "scoring/run_babylm_local_score.py", "--workspace", str(workspace),
                   "--output-score", str(output)]
    elif topic.id == "mountaincar_continuous":
        command = [python, "scoring/run_mountaincar_continuous_score.py", "--workspace", str(workspace),
                   "--dataset-root", str(dataset), "--output-score", str(output)]
    elif topic.id == "arc_wbe_2026":
        command = [python, "scoring/run_arc_wbe_2026_local_score.py", "--workspace", str(workspace),
                   "--dataset-root", str(dataset / "visible-validation"), "--output-score", str(output)]
    elif topic.id == "tdc_admet_tox" and (workspace / "validation_predictions.csv").is_file():
        command = [python, "scoring/run_tdc_admet_tox_validation_score.py", "--validation", str(dataset / "public/validation.csv"),
                   "--predictions", str(workspace / "validation_predictions.csv"), "--output-metrics", str(output)]
    else:
        return None
    if topic.id not in {"mountaincar_continuous", "arc_wbe_2026"}:
        path = workspace / ("predictions.jsonl" if topic.id == "psydefdetect" else
                            "validation_predictions.csv" if topic.id == "tdc_admet_tox" else "experiment_trace.json")
        if path.is_symlink() or not path.is_file():
            raise ArenaError(f"Local scorer requires a regular file: {path.name}")
    check_call(command, "Local score", timeout=3600)
    return output.name


def run_pair(topic: Topic, adapter: dict, route: dict, batch: Path,
             paths: tuple[Path, Path, int], provider: dict) -> dict:
    data_dir, cache, timeout = paths
    run = batch / f"{topic.id}--{adapter['id']}"
    workspace = run / "workspace"
    workspace.mkdir(parents=True)
    # The sandbox may use a different uid. The enclosing batch stays private.
    workspace.chmod(0o777)
    (workspace / ".home").mkdir(mode=0o777)
    (workspace / ".home").chmod(0o777)
    inputs = run / "input"
    inputs.mkdir()
    (run / "logs").mkdir()
    try:
        dataset = prepare_dataset(topic, data_dir)
        visible = project_visible_dataset(topic, dataset, run)
        contract = topic.contract.read_text(encoding="utf-8")
        budget_path = ROOT / "contracts" / f"{topic.id}_execution_budget.md"
        if budget_path.is_file():
            contract = f"{contract.rstrip()}\n\n{budget_path.read_text(encoding='utf-8')}"
        (inputs / "prompt.txt").write_text(contract, encoding="utf-8")
        if topic.id == "psydefdetect":
            shutil.copyfile(ROOT / "psydefdetect_split.canonical.json", inputs / "psydefdetect_split.canonical.json")
        image = prepare_image(adapter, route, cache)
        name = "rceval-" + uuid.uuid4().hex[:16]
        args = docker_command(name, route, image, adapter["directory"], workspace, inputs, visible)
        log = launch(args, name, topic, run, provider, timeout)
        if route["native_marker"] not in log:
            raise ArenaError("Expected native log marker is missing")
        trace = require_artifacts(topic, workspace)
        if trace.get("framework_internal_model") != provider["OPENAI_MODEL"]:
            raise ArenaError("Trace model does not match the configured model")
        if str(trace.get("framework_internal_api_base_url", "")).rstrip("/") != provider["OPENAI_BASE_URL"].rstrip("/"):
            raise ArenaError("Trace endpoint does not match the configured endpoint")
    except (ArenaError, OSError, subprocess.SubprocessError, ValueError) as exc:
        return {"status": "failed", "reason": str(exc), "directory": str(run), "scored": False}
    try:
        local_metrics = score_local(topic, workspace, dataset, run)
    except (ArenaError, OSError, ValueError) as exc:
        return {"status": "score_failed", "reason": str(exc), "directory": str(run), "scored": False}
    return {"status": "completed", "directory": str(run), "scored": bool(local_metrics),
            "local_metrics": local_metrics, "model": provider["OPENAI_MODEL"],
            "upstream_commit": adapter.get("upstream_commit"), "image": image}


def run_batch(pairs: list, batch: Path, paths: tuple[Path, Path, int], provider: dict) -> list:
    rows = []
    for topic, adapter, route in pairs:
        context = {"topic": topic.id, "framework": adapter["id"]}
        if "reason" in route:
            outcome = {"status": "unsupported", "reason": route["reason"]}
        else:
            print(f"Running {topic.id} / {adapter['id']}", file=sys.stderr, flush=True)
            try:
                outcome = run_pair(topic, adapter, route, batch, paths, provider)
            except (ArenaError, OSError, subprocess.SubprocessError, ValueError) as exc:
                outcome = {"status": "failed", "reason": str(exc)}
        rows.append(context | outcome)
        write_json(batch / "summary.json", rows)
    return rows


def parser() -> argparse.ArgumentParser:
    args = argparse.ArgumentParser(description=__doc__)
    commands = args.add_subparsers(dest="action", required=True)
    commands.add_parser("list", help="List tasks, frameworks and route status")
    run = commands.add_parser("run", help="Run one framework across tasks, or one task across frameworks")
    run.add_argument("--topic", choices=(*TOPICS, "all"), required=True)
    choice = run.add_mutually_exclusive_group(required=True)
    choice.add_argument("--framework", help="Built-in framework ID or all")
    choice.add_argument("--adapter", type=Path, help="Directory containing a local adapter.json")
    run.add_argument("--dry-run", action="store_true", help="Show selected routes without setup or credentials")
    run.add_argument("--env-file", type=Path, help="Plain API environment assignments, not a shell script")
    run.add_argument("--data-dir", type=Path, default=ROOT / "data")
    run.add_argument("--run-dir", type=Path, default=ROOT / "runs")
    run.add_argument("--timeout", type=int, default=7200, help="Per-run container timeout in seconds")
    return args


def main(argv: list[str] | None = None) -> int:
    arg_parser = parser()
    args = arg_parser.parse_args(argv)
    try:
        builtins = load_builtins()
        if args.action == "list":
            print(json.dumps({"topics": [{"id": t.id, "name": t.label} for t in TOPICS.values()],
                              "frameworks": [{"id": a["id"], "name": a["name"], "routes": [
                                  describe_pair(t, a, get_route(a, t)) for t in TOPICS.values()]}
                                  for a in builtins.values()]}, ensure_ascii=False, indent=2))
            return 0
        if args.topic == args.framework == "all":
            arg_parser.error("select a specific topic or a specific framework")
        if args.timeout <= 0:
            arg_parser.error("--timeout must be positive")
        topics = list(TOPICS.values()) if args.topic == "all" else [TOPICS[args.topic]]
        if args.adapter is not None:
            adapters = [load_adapter(args.adapter, builtin=False)]
        elif args.framework == "all":
            adapters = list(builtins.values())
        elif args.framework in builtins:
            adapters = [builtins[args.framework]]
        else:
            arg_parser.error(f"unknown framework {args.framework!r}; see list")
        pairs = [(topic, adapter, get_route(adapter, topic)) for topic in topics for adapter in adapters]
        if not pairs:
            raise ArenaError("The selected batch is empty")
        if args.dry_run:
            print(json.dumps([describe_pair(*pair) for pair in pairs], indent=2))
            return 0
        runnable = any("reason" not in route for _, _, route in pairs)
        default_env = ROOT / ".env"
        env_file = args.env_file if args.env_file else default_env if default_env.is_file() else None
        provider = provider_env(env_file) if runnable else {}
        if runnable:
            check_call(["docker", "info", "--format", "{{.ServerVersion}}"], "Check Docker", timeout=30, quiet=True)
        data_dir = args.data_dir.resolve()
        data_dir.mkdir(parents=True, exist_ok=True)
        cache = data_dir / ".arena-cache"
        cache.mkdir(exist_ok=True)
        run_dir = args.run_dir.resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        batch = Path(tempfile.mkdtemp(prefix="arena-", dir=run_dir))
        outcomes = run_batch(pairs, batch, (data_dir, cache, args.timeout), provider)
        print(f"Batch summary: {batch / 'summary.json'}")
        return 0 if all(row["status"] == "completed" for row in outcomes) else 1
    except (ArenaError, OSError, ValueError) as exc:
        print(f"Arena: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Arena: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
