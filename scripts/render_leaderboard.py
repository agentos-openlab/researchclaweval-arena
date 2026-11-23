#!/usr/bin/env python3
"""Render the public leaderboard from reviewed, sanitized historical evidence."""

from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TOPICS = {
    "arc_wbe_2026": ("ARC-WBE-2026", "Adjusted final-layer score", True),
    "babylm": ("BabyLM-10M", "Validation perplexity", True),
    "mountaincar_continuous": ("MountainCar-Continuous", "Mean reward", False),
    "psydefdetect": ("PsyDefDetect", "Macro-F1 over classes 1–8", False),
    "tdc_admet_tox": ("TDC-ADMET-Tox", "Macro-AUROC", False),
}
STATUSES = {"verified", "self_reported", "unverified", "missing"}
FIELDS = (
    "topic", "model", "protocol", "framework", "rank", "value", "status", "reviewed_runs", "source_sha256"
)
SHA256 = re.compile(r"[0-9a-f]{64}")


def group_key(row: dict) -> tuple:
    return row["topic"], row["model"], row["protocol"]


def validate(row: dict) -> None:
    for key in ("model", "framework", "protocol"):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip() or any(char in value for char in "\r\n|"):
            raise ValueError(f"invalid {key}")
    topic, status = row.get("topic"), row.get("status")
    if topic not in TOPICS or status not in STATUSES:
        raise ValueError(f"unknown topic or result status: {topic}, {status}")
    if (status == "verified" and topic == "babylm") or (status == "self_reported" and topic != "babylm"):
        raise ValueError("BabyLM historical scores are self-reported and unranked")
    value, digest, count = row.get("value"), row.get("source_sha256"), row.get("reviewed_runs")
    if type(count) is not int or count < 0:
        raise ValueError("reviewed_runs must be a nonnegative integer")
    if status in {"verified", "self_reported"}:
        if type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("published scores require a finite number")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest) or count < 1:
            raise ValueError("published scores require a source SHA-256 and a reviewed observation")
    elif value is not None or digest is not None or count != 0:
        raise ValueError("missing and unverified rows must have no score or score source")


def rank(entries: list[dict]) -> list[dict]:
    seen = set()
    for row in entries:
        validate(row)
        key = (*group_key(row), row["framework"])
        if key in seen:
            raise ValueError(f"duplicate historical evidence row: {key}")
        seen.add(key)
    output = []
    for (topic, _, _), group in itertools.groupby(sorted(entries, key=group_key), group_key):
        rows = list(group)
        direction = 1 if TOPICS[topic][2] else -1
        verified = sorted(
            (row for row in rows if row["status"] == "verified"),
            key=lambda row: (direction * row["value"], row["framework"]),
        )
        previous_score = None
        current_rank = None
        for position, row in enumerate(verified, start=1):
            if row["value"] != previous_score:
                current_rank = position
                previous_score = row["value"]
            output.append({**row, "rank": current_rank})
        output.extend(
            {**row, "rank": None}
            for row in sorted(rows, key=lambda row: row["framework"])
            if row["status"] != "verified"
        )
    return output


def csv_text(rows: list[dict]) -> str:
    sink = io.StringIO(newline="")
    writer = csv.DictWriter(sink, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row[field] for field in FIELDS} for row in rows)
    return sink.getvalue()


def markdown_text(rows: list[dict], snapshot: dict) -> str:
    lines = [
        "# Historical benchmark leaderboard", "",
        f"Paper snapshot: {snapshot['paper_version']}. "
        f"Reviewed score cells: {sum(r['status'] == 'verified' for r in rows)} ranked and "
        f"{sum(r['status'] == 'self_reported' for r in rows)} self-reported.", "",
        "Rankings compare frameworks within a task, model and evaluation protocol. Ties share a rank. "
        "The review covers selected paper observations, so the reviewed run count is a lower bound. "
        "A blank score denotes a missing or unverified observation. "
        "The [review method](README.md) describes the acceptance criteria.", "",
        "[Download CSV](leaderboard.csv) · [Paper snapshot data](../website/data/runs.json)", "",
    ]
    for topic, topic_rows in itertools.groupby(rows, key=lambda row: row["topic"]):
        name, metric, lower = TOPICS[topic]
        lines.extend([f"## {name}", "", f"{metric} ({'lower' if lower else 'higher'} is better).", ""])
        if topic == "babylm":
            lines.extend(["Framework-reported perplexity is shown for reference. "
                          "The shared-reference and framework-specific protocols are listed separately.", ""])
        for (_, model, protocol), group in itertools.groupby(topic_rows, group_key):
            lines.extend([f"### {model} · {protocol}", "", "| Rank | Framework | Score | Status |",
                          "|---:|---|---:|---|"])
            for row in group:
                score = "—" if row["value"] is None else str(row["value"])
                lines.append(f"| {row['rank'] or '—'} | {row['framework']} | {score} | "
                             f"{row['status'].replace('_', ' ')} |")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args()
    snapshot = json.loads((RESULTS / "historical-evidence.json").read_text(encoding="utf-8"))
    rows = rank(snapshot["entries"])
    artifacts = {"leaderboard.csv": csv_text(rows), "leaderboard.md": markdown_text(rows, snapshot)}
    for name, content in artifacts.items():
        path = RESULTS / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                parser.exit(1, f"stale leaderboard output: {name}\n")
        else:
            path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
