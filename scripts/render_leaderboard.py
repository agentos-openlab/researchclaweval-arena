#!/usr/bin/env python3
"""Render the public leaderboard from reviewed, sanitized historical evidence."""

from __future__ import annotations

import argparse
import csv
import html
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
TOPICS_ZH = {
    "arc_wbe_2026": ("ARC-WBE-2026", "调整后的末层得分", True),
    "babylm": ("BabyLM-10M", "验证集困惑度", True),
    "mountaincar_continuous": ("MountainCar-Continuous", "平均奖励", False),
    "psydefdetect": ("PsyDefDetect", "类别 1–8 的 Macro-F1", False),
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
        "These are historical records, not official competition standings. "
        "The [review method](README.md) describes the acceptance criteria.", "",
        "[ARC-WBE-2026](#arc-wbe-2026) · [BabyLM-10M](#babylm-10m) · "
        "[MountainCar-Continuous](#mountaincar-continuous) · [PsyDefDetect](#psydefdetect) · "
        "[TDC-ADMET-Tox](#tdc-admet-tox)", "",
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


def markdown_text_zh(rows: list[dict], snapshot: dict) -> str:
    lines = [
        "# 历史评测榜单", "",
        f"论文数据快照：{snapshot['paper_version']}。经复核的评分记录："
        f"{sum(r['status'] == 'verified' for r in rows)} 条有名次，"
        f"{sum(r['status'] == 'self_reported' for r in rows)} 条框架自报。", "",
        "榜单按任务、模型和评测协议分别比较框架。同分并列。复核范围为论文快照中选取的记录，"
        "因此复核运行数是下限。缺失或未核验记录不显示分数。这些是历史记录，不是正式比赛排名。"
        "复核标准见[结果说明](README.md)。", "",
        "[ARC-WBE-2026](#arc-wbe-2026) · [BabyLM-10M](#babylm-10m) · "
        "[MountainCar-Continuous](#mountaincar-continuous) · [PsyDefDetect](#psydefdetect) · "
        "[TDC-ADMET-Tox](#tdc-admet-tox)", "",
        "[下载完整 CSV](leaderboard.csv) · [论文快照数据](../website/data/runs.json)", "",
    ]
    status_names = {
        "verified": "已核验",
        "self_reported": "框架自报",
        "unverified": "未核验",
        "missing": "缺失",
    }
    for topic, topic_rows in itertools.groupby(rows, key=lambda row: row["topic"]):
        name, metric, lower = TOPICS_ZH[topic]
        lines.extend([f"## {name}", "", f"{metric}（{'越低' if lower else '越高'}越好）。", ""])
        if topic == "babylm":
            lines.extend(["框架报告的困惑度仅供参考。共享参考协议与框架自有协议分别列出，均不参与排名。", ""])
        for (_, model, protocol), group in itertools.groupby(topic_rows, group_key):
            lines.extend([f"### {model} · {protocol}", "", "| 名次 | 框架 | 得分 | 状态 |", "|---:|---|---:|---|"])
            for row in group:
                score = "—" if row["value"] is None else str(row["value"])
                lines.append(f"| {row['rank'] or '—'} | {row['framework']} | {score} | {status_names[row['status']]} |")
            lines.append("")
    return "\n".join(lines)


def readme_figure_svg(snapshot: dict) -> str:
    """Render the leaderboard's six-dimensional process-profile radar chart."""
    width, height = 1440, 930
    profile_data = json.loads((ROOT / "website/data/leaderboard.json").read_text(encoding="utf-8"))["items"]
    framework_data = json.loads((ROOT / "website/data/frameworks.json").read_text(encoding="utf-8"))["items"]
    framework_names = {entry["id"]: entry["name"] for entry in framework_data}
    profiles = profile_data["profiles"]
    dimensions = [
        "Plan quality",
        "Plan–execution alignment",
        "Execution robustness",
        "Observation use",
        "Evidence–conclusion closure",
        "State consistency",
    ]
    colors = ["#1a4b7c", "#a76931", "#457d71", "#854b68", "#687caa", "#9a763b", "#667682"]

    def text(
        x: float,
        y: float,
        value: str,
        *,
        size: int = 13,
        color: str = "#24384a",
        weight: str = "400",
        anchor: str = "start",
    ) -> str:
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'
        )

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">ResearchClawEval six-dimensional process profiles</title>',
        '<desc id="desc">A radar chart showing six historical Judge-coded process-profile dimensions for seven frameworks. The dimensions are descriptive and do not form an overall ranking.</desc>',
        '<rect width="100%" height="100%" fill="#f4f7fa"/>',
        text(60, 48, "RESEARCHCLAW EVAL ARENA · HISTORICAL RESULTS", size=12, color="#397e78", weight="700"),
        text(60, 96, "Research process profiles", size=36, color="#183149", weight="700"),
        text(60, 128, f"Paper snapshot {snapshot['paper_version']} · seven frameworks · scale 0–1", size=15, color="#61788a"),
        '<rect x="60" y="158" width="1320" height="744" rx="14" fill="#ffffff" stroke="#dce5ec"/>',
        text(90, 202, "Six Judge-coded dimensions · common cohort of 10 conditions", size=14, color="#61788a"),
    ]

    center_x, center_y, radius = 720.0, 505.0, 232.0
    angles = [-math.pi / 2 + index * math.tau / len(dimensions) for index in range(len(dimensions))]
    for step in range(5, 0, -1):
        scale = step / 5
        ring_points = " ".join(
            f"{center_x + radius * scale * math.cos(angle):.1f},{center_y + radius * scale * math.sin(angle):.1f}"
            for angle in angles
        )
        fill = "#f4f8fb" if step % 2 else "#ffffff"
        pieces.append(f'<polygon points="{ring_points}" fill="{fill}" stroke="#dce5ec" stroke-width="1"/>')

    for index, angle in enumerate(angles):
        x_end = center_x + radius * math.cos(angle)
        y_end = center_y + radius * math.sin(angle)
        pieces.append(
            f'<line x1="{center_x:.1f}" y1="{center_y:.1f}" x2="{x_end:.1f}" y2="{y_end:.1f}" stroke="#dce5ec"/>'
        )
        label_radius = radius + 34
        label_x = center_x + label_radius * math.cos(angle)
        label_y = center_y + label_radius * math.sin(angle) + 4
        anchor = "start" if math.cos(angle) > 0.2 else "end" if math.cos(angle) < -0.2 else "middle"
        pieces.append(text(label_x, label_y, dimensions[index], size=14, color="#4f6576", weight="700", anchor=anchor))

    for index, profile in enumerate(profiles):
        framework = framework_names[profile["frameworkId"]]
        if framework == "DrClaw":
            framework = "Dr. Claw"
        color = colors[index % len(colors)]
        values = profile["values"]
        polygon_points = " ".join(
            f"{center_x + radius * value * math.cos(angle):.1f},{center_y + radius * value * math.sin(angle):.1f}"
            for value, angle in zip(values, angles, strict=True)
        )
        pieces.append(
            f'<polygon points="{polygon_points}" fill="{color}" fill-opacity="0.07" '
            f'stroke="{color}" stroke-width="2" stroke-opacity="0.82"/>'
        )
        for value, angle in zip(values, angles, strict=True):
            point_x = center_x + radius * value * math.cos(angle)
            point_y = center_y + radius * value * math.sin(angle)
            pieces.append(f'<circle cx="{point_x:.1f}" cy="{point_y:.1f}" r="2.8" fill="{color}"/>')
        legend_x = (210 + index * 300) if index < 4 else (360 + (index - 4) * 300)
        legend_y = 832 if index < 4 else 862
        pieces.append(f'<circle cx="{legend_x}" cy="{legend_y - 4}" r="4" fill="{color}"/>')
        pieces.append(text(legend_x + 10, legend_y, framework, size=12, color="#40576a"))

    pieces.extend([
        text(90, 890, "Ordinal process means; descriptive profiles, not an overall ranking.", size=11, color="#667d8d"),
        '</svg>',
    ])
    return "\n".join(pieces) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args()
    snapshot = json.loads((RESULTS / "historical-evidence.json").read_text(encoding="utf-8"))
    rows = rank(snapshot["entries"])
    artifacts = {
        "leaderboard.csv": csv_text(rows),
        "leaderboard.md": markdown_text(rows, snapshot),
        "leaderboard.zh-CN.md": markdown_text_zh(rows, snapshot),
    }
    for name, content in artifacts.items():
        path = RESULTS / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                parser.exit(1, f"stale leaderboard output: {name}\n")
        else:
            path.write_text(content, encoding="utf-8")
    figure_path = ROOT / "assets" / "leaderboard-snapshot.svg"
    figure_content = readme_figure_svg(snapshot)
    if args.check:
        if not figure_path.is_file() or figure_path.read_text(encoding="utf-8") != figure_content:
            parser.exit(1, f"stale leaderboard output: {figure_path.relative_to(ROOT)}\n")
    else:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure_path.write_text(figure_content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
