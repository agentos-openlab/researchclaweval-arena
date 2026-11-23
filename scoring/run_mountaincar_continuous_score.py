#!/usr/bin/env python3
"""Score five MountainCar checkpoints using the pinned upstream evaluator in Docker."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from prepare_public_topic_data import (
    MOUNTAINCAR_EVALUATOR,
    MOUNTAINCAR_FILES,
    MOUNTAINCAR_REVISION,
    sha256_file,
)

DOCKERFILE = Path(__file__).with_name("mountaincar_continuous.Dockerfile")


def require_local(path: Path, *, directory: bool = False) -> None:
    if path.is_symlink():
        raise ValueError(f"symbolic link in score inputs: {path}")
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f"required {'directory' if directory else 'file'} missing: {path}")


def stage_payload(workspace: Path, staging: Path) -> None:
    require_local(workspace, directory=True)
    config = workspace / "config.yaml"
    source = workspace / "src"
    checkpoint_root = workspace / "checkpoints"
    require_local(config)
    require_local(source, directory=True)
    require_local(checkpoint_root, directory=True)
    checkpoints = sorted(checkpoint_root.glob("*.pkl"))
    if len(checkpoints) != 5 or not all(path.name.startswith("config") for path in checkpoints):
        raise ValueError("expected exactly five checkpoints named config*.pkl")
    for path in checkpoints:
        require_local(path)
    for path in source.rglob("*"):
        require_local(path, directory=path.is_dir())
    shutil.copyfile(config, staging / config.name)
    shutil.copytree(source, staging / source.name, dirs_exist_ok=True)
    (staging / checkpoint_root.name).mkdir(exist_ok=True)
    for path in checkpoints:
        shutil.copyfile(path, staging / checkpoint_root.name / path.name)


def evaluator_command(payload: Path, evaluator: Path, image: str, name: str) -> list[str]:
    if "," in str(payload) or "," in str(evaluator):
        raise ValueError("Docker input mount paths must not contain commas")
    affinity = getattr(os, "sched_getaffinity", None)
    cpu_args = ["--cpuset-cpus", ",".join(map(str, sorted(affinity(0))[:2]))] if affinity else []
    return [
        "docker", "run", "--pull=never", "--rm", "--name", name, "--network", "none",
        "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=256",
        "--memory=8g", "--cpus=2", *cpu_args,
        "--user", f"{os.getuid()}:{os.getgid()}" if os.getuid() else "65534:65534",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=512m", "--workdir", "/submission",
        "--mount", f"type=bind,source={payload},target=/submission,readonly",
        "--mount", f"type=bind,source={evaluator},target=/evaluator/evaluate.py,readonly",
        "--env", "HOME=/tmp", "--env", "PYTHONPATH=/submission", "--env", "JAX_PLATFORMS=cpu",
        "--env", "OPENBLAS_NUM_THREADS=1", "--env", "OMP_NUM_THREADS=2",
        "--entrypoint", "python", image, "-B", "/evaluator/evaluate.py", "--config_fname", "config.yaml",
    ]


def parse_score(stdout: str) -> tuple[float, float]:
    for line in reversed(stdout.splitlines()):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict) or "Reward Mean" not in row or "Reward Std" not in row:
            continue
        mean, stdev = row["Reward Mean"], row["Reward Std"]
        if all(type(value) in (int, float) and math.isfinite(value) for value in (mean, stdev)) and stdev >= 0:
            return float(mean), float(stdev)
        break
    raise ValueError("evaluator did not report valid Reward Mean and Reward Std metrics")


def evaluator_image() -> str:
    image = f"rceval/mountaincar-scorer:{sha256_file(DOCKERFILE)[:12]}"
    if subprocess.run(["docker", "image", "inspect", image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        with tempfile.TemporaryDirectory() as context:
            subprocess.run(["docker", "build", "--tag", image, "--file", str(DOCKERFILE), context], check=True, timeout=900)
    return image


def score_run(workspace: Path, dataset_root: Path) -> dict:
    evaluator = dataset_root / MOUNTAINCAR_EVALUATOR
    require_local(evaluator)
    digest = MOUNTAINCAR_FILES[MOUNTAINCAR_EVALUATOR]
    if sha256_file(evaluator) != digest:
        raise ValueError("upstream evaluator failed SHA-256 verification")
    name = f"arena-mountaincar-score-{uuid.uuid4().hex}"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "submission"
        work.mkdir(mode=0o755)
        stage_payload(workspace, work)
        for path in work.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        staged_evaluator = work / "_upstream_evaluate.py"
        shutil.copyfile(evaluator, staged_evaluator)
        staged_evaluator.chmod(0o644)
        if sha256_file(staged_evaluator) != digest:
            raise ValueError("staged evaluator failed SHA-256 verification")
        command = evaluator_command(work, staged_evaluator, evaluator_image(), name)
        with tempfile.TemporaryFile() as log:
            try:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=600)
            except subprocess.TimeoutExpired:
                subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                raise
            log.seek(max(0, log.tell() - 64 * 1024))
            output = log.read().decode("utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(f"evaluator exited with status {result.returncode}: {output[-2000:]}")
        mean, stdev = parse_score(output)
    return {
        "task_id": "mountaincar_continuous", "metric": "Reward Mean", "score": mean, "reward_std": stdev,
        "score_source": "official_evaluate_py", "evaluator_revision": MOUNTAINCAR_REVISION,
        "evaluator_sha256": digest, "checkpoint_count": 5, "scope": "local_reproduction",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-score", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.output_score.exists() or args.output_score.is_symlink():
            raise FileExistsError(f"score output already exists: {args.output_score}")
        score = score_run(args.workspace.absolute(), args.dataset_root.absolute())
        rendered = json.dumps(score, allow_nan=False)
        args.output_score.parent.mkdir(parents=True, exist_ok=True)
        with args.output_score.open("x", encoding="utf-8") as output:
            output.write(rendered + "\n")
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"{exc}\n")
    print(rendered)


if __name__ == "__main__":
    main()
