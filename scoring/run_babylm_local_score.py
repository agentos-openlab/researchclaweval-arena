#!/usr/bin/env python3
"""Extract a self-reported BabyLM score from the selected experiment."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def diagnostic_score(trace: dict) -> dict:
    selected_id = trace.get("selected_experiment_id")
    experiments = trace.get("experiments")
    if not isinstance(selected_id, str) or not selected_id or not isinstance(experiments, list):
        raise ValueError("trace must specify selected_experiment_id and experiments")
    matches = [row for row in experiments if isinstance(row, dict) and row.get("experiment_id") == selected_id]
    if len(matches) != 1:
        raise ValueError("trace must have exactly one selected experiment")
    value = matches[0].get("validation_perplexity")
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError("selected experiment needs a positive finite validation_perplexity")
    return {
        "task_id": "babylm",
        "metric": "word_level_validation_perplexity",
        "score": value,
        "score_source": "framework_self_reported",
        "rank_eligible": False,
        "selected_experiment_id": selected_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output-score", required=True, type=Path)
    args = parser.parse_args()
    try:
        trace = json.loads((args.workspace / "experiment_trace.json").read_text(encoding="utf-8"))
        if not isinstance(trace, dict):
            raise ValueError("experiment_trace.json must contain an object")
        rendered = json.dumps(diagnostic_score(trace), allow_nan=False)
        args.output_score.parent.mkdir(parents=True, exist_ok=True)
        with args.output_score.open("x", encoding="utf-8") as output:
            output.write(rendered + "\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(rendered)


if __name__ == "__main__":
    main()
