#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scoring"))

SCORING_DIR = ROOT / "scoring"
DOCKERFILE = SCORING_DIR / "arc_wbe_2026_scorer.Dockerfile"

from arc_wbe_2026_official_adapter import (  # noqa: E402
    materialize_official_adapter,
    scan_workspace_for_official_adapter,
)
from prepare_arc_wbe_2026_dataset import (  # noqa: E402
    MANIFEST_NAME,
    baked_split_dir,
    default_whest_python,
)

OFFICIAL_ADAPTER_SCORE_SOURCES = {
    "official_adapter_whest_run",
}

LOCAL_OFFICIAL_EVAL_SCORE_SOURCES = {
    "local_official_eval",
    "local_official_eval_adjusted_final_layer_score",
    "local_official_eval_reconstructed_from_per_mlp",
    "local_official_eval_stdout",
}


def try_generate_official_adapter(
    workspace: Path,
    framework_hint: str | None,
    output_dir: Path,
) -> tuple[Path | None, dict[str, object] | None]:
    try:
        scan_result = scan_workspace_for_official_adapter(workspace, framework_hint=framework_hint)
    except Exception:
        return None, None
    adapter_path = materialize_official_adapter(scan_result, output_dir)
    return adapter_path, scan_result


def build_adapter_output_root(base_root: Path, workspace: Path, framework_hint: str | None) -> Path:
    workspace_resolved = workspace.resolve()
    hint = framework_hint or "unknown"
    digest = hashlib.sha256(f"{hint}:{workspace_resolved}".encode("utf-8")).hexdigest()[:12]
    return base_root / f"generated_official_adapter_{digest}"


def read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def reconstruct_adjusted_score_from_results(results: object) -> float | None:
    if not isinstance(results, dict):
        return None
    per_mlp = results.get("per_mlp")
    if not isinstance(per_mlp, list) or not per_mlp:
        return None

    adjusted_scores: list[float] = []
    for row in per_mlp:
        if not isinstance(row, dict):
            return None
        final_mse = row.get("final_mse")
        if not is_number(final_mse):
            return None

        budget_exhausted = bool(row.get("budget_exhausted"))
        time_exhausted = bool(row.get("time_exhausted"))
        residual_wall_time_exhausted = bool(row.get("residual_wall_time_exhausted"))
        if budget_exhausted or time_exhausted or residual_wall_time_exhausted:
            multiplier = 1.0
        else:
            flops_used = row.get("flops_used")
            breakdowns = row.get("breakdowns")
            estimator = breakdowns.get("estimator") if isinstance(breakdowns, dict) else None
            flop_budget = estimator.get("flop_budget") if isinstance(estimator, dict) else None
            if not is_number(flops_used) or not is_number(flop_budget) or flop_budget <= 0:
                return None
            multiplier = max(0.1, float(flops_used) / float(flop_budget))

        adjusted_scores.append(float(final_mse) * multiplier)

    if not adjusted_scores:
        return None
    return sum(adjusted_scores) / len(adjusted_scores)


def extract_score_dict(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    if is_number(payload.get("score")):
        result = {"score": float(payload["score"])}
        if isinstance(payload.get("score_source"), str):
            result["score_source"] = payload["score_source"]
        return result

    results = payload.get("results")
    if isinstance(results, dict) and is_number(results.get("adjusted_final_layer_score")):
        return {
            "score": float(results["adjusted_final_layer_score"]),
            "score_source": "local_official_eval_adjusted_final_layer_score",
        }
    reconstructed = reconstruct_adjusted_score_from_results(results)
    if reconstructed is not None:
        return {
            "score": reconstructed,
            "score_source": "local_official_eval_reconstructed_from_per_mlp",
        }
    return None


def score_source_priority(payload: dict[str, object]) -> int:
    source = payload.get("score_source")
    if isinstance(source, str) and source in OFFICIAL_ADAPTER_SCORE_SOURCES:
        return 2
    if isinstance(source, str) and source in LOCAL_OFFICIAL_EVAL_SCORE_SOURCES:
        return 1
    return 0


def find_estimator_candidates(workspace: Path) -> list[Path]:
    candidates: list[Path] = []
    submission_payload = read_json(workspace / "submission.json")
    if isinstance(submission_payload, dict):
        explicit = submission_payload.get("estimator_artifact")
        if isinstance(explicit, str):
            explicit_path = Path(explicit)
            if explicit_path.exists():
                candidates.append(explicit_path)
        listed = submission_payload.get("estimator_candidates")
        if isinstance(listed, list):
            for item in listed:
                if not isinstance(item, str):
                    continue
                candidate = Path(item)
                if candidate.exists() and candidate not in candidates:
                    candidates.append(candidate)

    preferred = [
        workspace / "estimator.py",
        workspace / "submission" / "estimator.py",
        workspace / "artifacts" / "estimator.py",
    ]
    for path in preferred:
        if path.exists():
            candidates.append(path)

    for pattern in ("**/estimator.py", "**/*estimator*.py"):
        for path in sorted(workspace.glob(pattern)):
            if not path.is_file() or path in candidates:
                continue
            if any(part.startswith(".") for part in path.relative_to(workspace).parts):
                continue
            candidates.append(path)
    return candidates


def extract_score_payload(search_root: Path) -> tuple[Path | None, dict | None]:
    hits: list[tuple[Path, dict]] = []
    for path in search_root.rglob("*.json"):
        try:
            rel = path.relative_to(search_root)
        except Exception:
            rel = path
        if any(part.startswith(".") for part in rel.parts):
            continue
        payload = read_json(path)
        result = extract_score_dict(payload)
        if result is not None:
            hits.append((path, result))
    if not hits:
        return None, None
    best = max(
        hits,
        key=lambda item: (
            score_source_priority(item[1]),
            item[0].stat().st_mtime_ns,
            item[0].stat().st_ctime_ns,
            len(item[0].parts),
            str(item[0]),
        ),
    )
    return best


def infer_split_name(dataset_root: Path) -> str | None:
    name = dataset_root.name
    if name in {"mini", "full"}:
        return name
    if name == "arc-whestbench-full":
        return "full"
    if name == "arc-whestbench-mini":
        return "mini"
    manifest = dataset_root / MANIFEST_NAME
    if manifest.exists():
        payload = read_json(manifest)
        if isinstance(payload, dict):
            splits = payload.get("splits")
            if isinstance(splits, dict) and len(splits) == 1:
                return next(iter(splits.keys()))
    return None


def find_manifest_root(dataset_root: Path) -> Path | None:
    for candidate in (dataset_root, dataset_root.parent):
        if (candidate / MANIFEST_NAME).exists():
            return candidate
    return None


def resolve_dataset_root(dataset_root: Path) -> Path:
    if (dataset_root / "metadata.json").exists():
        return dataset_root
    manifest_root = find_manifest_root(dataset_root)
    split = infer_split_name(dataset_root)
    if manifest_root is not None and split is not None:
        payload = read_json(manifest_root / MANIFEST_NAME)
        if isinstance(payload, dict):
            splits = payload.get("splits")
            if isinstance(splits, dict):
                row = splits.get(split)
                if isinstance(row, dict):
                    baked_path = row.get("baked_path")
                    if isinstance(baked_path, str):
                        return Path(baked_path)
        return baked_split_dir(manifest_root, split)
    if (dataset_root / "dataset_info.json").exists():
        if split is not None and dataset_root.parent.name != "baked":
            return baked_split_dir(dataset_root.parent, split)
        return dataset_root
    full = dataset_root / "arc-whestbench-full"
    if full.exists() and (full / "dataset_info.json").exists():
        return resolve_dataset_root(full)
    return dataset_root


def ensure_dataset_root(
    dataset_root: Path,
    *,
    prepare_script: Path,
    whest_python: str,
) -> Path:
    resolved = resolve_dataset_root(dataset_root)
    if (resolved / "metadata.json").exists():
        return resolved

    manifest_root = find_manifest_root(dataset_root) or dataset_root
    split = infer_split_name(dataset_root)
    if split is None:
        return resolved

    subprocess.run(
        [
            sys.executable,
            str(prepare_script),
            "--output-root",
            str(manifest_root),
            "--splits",
            split,
            "--bake-splits",
            split,
            "--whest-python",
            whest_python,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    refreshed = resolve_dataset_root(dataset_root)
    return refreshed


def extract_score_from_stdout(stdout: str) -> dict | None:
    match = re.search(
        r"\bscore\b[^0-9-]*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)",
        stdout,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return {"score": float(match.group(1)), "score_source": "local_official_eval_stdout"}


def run_whest(
    *,
    whest_bin: str,
    estimator: Path,
    dataset_root: Path,
    runner: str,
    output_root: Path,
) -> tuple[Path | None, dict | None]:
    if shutil.which(whest_bin) is None:
        return None, None

    output_root.mkdir(parents=True, exist_ok=True)
    prepare_script = ROOT / "scoring" / "prepare_arc_wbe_2026_dataset.py"
    dataset_arg = ensure_dataset_root(
        dataset_root,
        prepare_script=prepare_script,
        whest_python=os.environ.get("ARC_WBE_2026_WHEST_PYTHON", default_whest_python()),
    ).resolve()
    metadata = read_json(dataset_arg / "metadata.json")
    if not isinstance(metadata, dict):
        raise RuntimeError("official scorer requires a materialized labeled ARC dataset")
    parquet_files = sorted((dataset_arg / "data").glob("*.parquet"))
    if not parquet_files:
        raise RuntimeError("official scorer found no materialized parquet records")
    import pyarrow.parquet as pq

    parquet_file = pq.ParquetFile(parquet_files[0])
    if parquet_file.metadata.num_rows <= 0:
        raise RuntimeError("official scorer found an empty ARC dataset")
    required_labels = {"weights", "all_layer_means", "final_means"}
    if not required_labels.issubset(set(parquet_file.schema_arrow.names)):
        raise RuntimeError("official scorer dataset is missing target labels")
    whest_env = os.environ.copy()
    whest_env.setdefault("HF_HOME", str((output_root / ".hf_home").resolve()))
    cmd = [
        whest_bin,
        "run",
        "--estimator",
        str(estimator.resolve()),
        "--dataset",
        str(dataset_arg),
        "--runner",
        runner,
    ]
    completed = subprocess.run(cmd, cwd=output_root, text=True, capture_output=True, env=whest_env)
    (output_root / "whest.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output_root / "whest.stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        return None, None

    artifact_path, payload = extract_score_payload(output_root)
    if artifact_path is not None and payload is not None:
        payload.setdefault("score_source", "local_official_eval")
        return artifact_path, payload

    payload = extract_score_from_stdout(completed.stdout)
    if payload is not None:
        return output_root / "whest.stdout.log", payload
    return None, None


def write_normalized_score(output_score: Path, artifact_path: Path, payload: dict) -> None:
    normalized = {
        "score": float(payload["score"]),
        "score_source": payload.get("score_source", "local_official_eval"),
        "score_artifact": str(artifact_path),
    }
    output_score.parent.mkdir(parents=True, exist_ok=True)
    output_score.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def scorer_image() -> str:
    signature = hashlib.sha256(
        DOCKERFILE.read_bytes() + (SCORING_DIR / "requirements.txt").read_bytes()
    ).hexdigest()[:12]
    image = f"rceval/arc-wbe-scorer:{signature}"
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if inspect.returncode:
        subprocess.run(
            ["docker", "build", "--file", str(DOCKERFILE), "--tag", image, str(SCORING_DIR)],
            check=True,
            timeout=1800,
        )
    return image


def isolated_scorer_command(
    *, workspace: Path, dataset_root: Path, output_root: Path, image: str, name: str
) -> list[str]:
    paths = (SCORING_DIR.resolve(), workspace.resolve(), dataset_root.resolve(), output_root.resolve())
    if any(any(char in str(path) for char in ',"\n\r') for path in paths):
        raise ValueError("Docker input and output paths cannot contain commas, quotes or newlines")
    scoring, workspace_path, dataset, output = map(str, paths)
    uid, gid = os.getuid(), os.getgid()
    return [
        "docker", "run", "--pull=never", "--rm", "--name", name,
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--pids-limit", "256",
        "--memory", "8g", "--cpus", "2", "--user", f"{uid}:{gid}",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=1g", "--workdir", "/arena",
        "--mount", f"type=bind,source={scoring},target=/arena/scoring,readonly",
        "--mount", f"type=bind,source={workspace_path},target=/workspace,readonly",
        "--mount", f"type=bind,source={dataset},target=/dataset,readonly",
        "--mount", f"type=bind,source={output},target=/output",
        "--env", "HOME=/tmp", "--env", "HF_HOME=/output/.hf_home",
        "--env", "ARENA_ARC_SCORER_CONTAINER=1", "--env", "PYTHONDONTWRITEBYTECODE=1",
        "--entrypoint", "python", image, "-B",
        "/arena/scoring/run_arc_wbe_2026_local_score.py",
        "--workspace", "/workspace", "--dataset-root", "/dataset",
        "--output-score", "/output/score.json",
        "--whest-output-root", "/output/whest_official_eval",
    ]


def run_isolated(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.dataset_root is None:
        parser.error("--dataset-root is required for isolated ARC scoring")
    for name, path in (("workspace", args.workspace), ("dataset root", args.dataset_root)):
        if path.is_symlink() or not path.is_dir():
            parser.error(f"{name} must be a real directory: {path}")
    if args.output_score.exists() or args.output_score.is_symlink():
        parser.error(f"refusing to overwrite score output: {args.output_score}")
    output_root = args.output_score.parent / "arc_wbe_scoring"
    if output_root.exists() or output_root.is_symlink():
        parser.error(f"refusing to overwrite scorer output directory: {output_root}")
    output_root.mkdir(parents=True, mode=0o777)
    output_root.chmod(0o777)
    name = f"arena-arc-score-{uuid.uuid4().hex}"
    try:
        command = isolated_scorer_command(
            workspace=args.workspace,
            dataset_root=args.dataset_root,
            output_root=output_root,
            image=scorer_image(),
            name=name,
        )
        completed = subprocess.run(command, text=True, capture_output=True, timeout=3600, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        subprocess.run(
            ["docker", "rm", "-f", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        parser.exit(1, f"isolated ARC scorer could not run: {exc}\n")
    (output_root / "container.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        parser.exit(1, f"isolated ARC scorer exited {completed.returncode}; see {output_root / 'container.log'}\n")
    inner_score = output_root / "score.json"
    if inner_score.is_symlink() or not inner_score.is_file():
        parser.exit(1, "isolated ARC scorer did not produce a regular score.json\n")
    payload = read_json(inner_score)
    if not isinstance(payload, dict) or not is_number(payload.get("score")):
        parser.exit(1, "isolated ARC scorer produced an invalid score.json\n")
    score_artifact = payload.get("score_artifact")
    if not isinstance(score_artifact, str):
        parser.exit(1, "isolated ARC scorer omitted score provenance\n")
    artifact_path = Path(score_artifact)
    try:
        relative = artifact_path.relative_to("/output")
    except ValueError:
        parser.exit(1, "isolated ARC scorer returned an unexpected score artifact path\n")
    local_artifact = output_root / relative
    if local_artifact.is_symlink() or not local_artifact.is_file():
        parser.exit(1, "isolated ARC scorer referenced a missing or unsafe artifact\n")
    payload["score_artifact"] = str(local_artifact)
    args.output_score.parent.mkdir(parents=True, exist_ok=True)
    with args.output_score.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
    print(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-score", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--framework-hint")
    parser.add_argument("--whest-bin", default="whest")
    parser.add_argument("--runner", default="local")
    parser.add_argument("--whest-output-root", type=Path)
    args = parser.parse_args(argv)

    if os.environ.get("ARENA_ARC_SCORER_CONTAINER") != "1":
        return run_isolated(args, parser)

    if args.output_score.exists():
        raise RuntimeError(
            "refusing to overwrite a framework-visible score.json; the host scorer must be the sole score owner"
        )
    whest_output_root = args.whest_output_root or (args.output_score.parent / "whest_official_eval")
    if whest_output_root.exists():
        raise RuntimeError(
            "refusing a pre-existing official scorer output directory; stale or framework-authored score evidence is inadmissible"
        )

    adapter_output_root = build_adapter_output_root(
        args.output_score.parent, args.workspace, args.framework_hint
    )
    adapter_estimator, _adapter_meta = try_generate_official_adapter(
        args.workspace,
        args.framework_hint,
        adapter_output_root,
    )
    if adapter_estimator is not None and args.dataset_root is not None:
        artifact_path, payload = run_whest(
            whest_bin=args.whest_bin,
            estimator=adapter_estimator,
            dataset_root=args.dataset_root,
            runner=args.runner,
            output_root=whest_output_root,
        )
        if artifact_path is not None and payload is not None:
            payload["score_source"] = "official_adapter_whest_run"
            write_normalized_score(args.output_score, artifact_path, payload)
            return 0

    raise RuntimeError("official adapter execution did not produce a real official score")


if __name__ == "__main__":
    raise SystemExit(main())
