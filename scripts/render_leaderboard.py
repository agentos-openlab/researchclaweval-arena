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


def readme_figure_svg(rows: list[dict], snapshot: dict) -> str:
    """Render an actual-score snapshot for the README from reviewed leaderboard rows."""
    featured_model = "GPT-5.6-Luna"
    width, height = 1800, 980
    margin, gap = 60, 24
    card_width = (width - 2 * margin - 2 * gap) // 3
    card_height = 344
    positions = [
        (margin + col * (card_width + gap), 180 + row * 368)
        for row in range(2)
        for col in range(3)
    ]
    verified_count = sum(row["status"] == "verified" for row in rows)
    self_reported_count = sum(row["status"] == "self_reported" for row in rows)
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">ResearchClawEval historical leaderboard snapshot</title>',
        '<desc id="desc">Actual GPT-5.6-Luna leaderboard results from the archived paper snapshot. Each topic is ranked independently, and BabyLM scores are marked unranked.</desc>',
        '<rect width="100%" height="100%" fill="#091724"/>',
        '<text x="60" y="47" fill="#7ddfc4" font-family="Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="2.2">RESEARCHCLAW EVAL ARENA · HISTORICAL RESULTS</text>',
        '<text x="60" y="100" fill="#f4f0e5" font-family="Arial,sans-serif" font-size="40" font-weight="700">Topic leaderboards</text>',
        f'<text x="60" y="137" fill="#9eb2c2" font-family="Arial,sans-serif" font-size="16">Selected model: {featured_model} · paper snapshot {html.escape(snapshot["paper_version"])} · scores are not compared across topics.</text>',
    ]

    def label(x: int, y: int, value: str, *, size: int = 13, color: str = "#edf3f5", weight: str = "400", anchor: str = "start") -> str:
        return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" '
                f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>')

    def score_text(value: float) -> str:
        return f"{value:.4f}"

    for topic_index, (topic, (name, metric, lower)) in enumerate(TOPICS.items()):
        x, y = positions[topic_index]
        topic_rows = [row for row in rows if row["topic"] == topic and row["model"] == featured_model]
        verified = sorted((row for row in topic_rows if row["status"] == "verified"), key=lambda row: row["rank"])
        shown = sorted((row for row in topic_rows if row["status"] == "self_reported"), key=lambda row: row["framework"])
        protocols = {row["protocol"] for row in verified}
        if topic != "babylm" and len(protocols) != 1:
            raise ValueError(f"README figure expects one reviewed protocol for {topic}, got {protocols}")
        protocol_label = ("Self-reported protocols shown separately" if topic == "babylm"
                          else next(iter(protocols), "No verified result"))

        pieces.extend([
            f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="16" fill="#11283a" stroke="#29465a" stroke-width="1.4"/>',
            label(x + 22, y + 35, name, size=20, color="#f4f0e5", weight="700"),
            label(x + 22, y + 61, f"{metric} · {'lower' if lower else 'higher'} is better", size=12, color="#9eb2c2"),
            label(x + 22, y + 84, protocol_label, size=11, color="#79cdb9"),
            f'<line x1="{x + 20}" y1="{y + 101}" x2="{x + card_width - 20}" y2="{y + 101}" stroke="#2a4558"/>',
        ])

        if topic == "babylm":
            pieces.extend([
                label(x + 22, y + 124, "FRAMEWORK · PROTOCOL", size=10, color="#829aaa", weight="700"),
                label(x + card_width - 94, y + 124, "SCORE", size=10, color="#829aaa", weight="700", anchor="end"),
                label(x + card_width - 22, y + 124, "STATUS", size=10, color="#829aaa", weight="700", anchor="end"),
            ])
            for index, row in enumerate(shown):
                row_y = y + 153 + index * 42
                proto = "shared reference" if "Shared-reference" in row["protocol"] else "framework-specific"
                pieces.extend([
                    label(x + 22, row_y, f"{row['framework']} · {proto}", size=12, color="#edf3f5"),
                    label(x + card_width - 94, row_y, score_text(row["value"]), size=12, color="#f0c975", weight="700", anchor="end"),
                    label(x + card_width - 22, row_y, "unranked", size=10, color="#f0c975", anchor="end"),
                ])
            if not shown:
                pieces.append(label(x + 22, y + 158, "No framework-reported score for this model", size=12, color="#b0bdc6"))
        else:
            pieces.extend([
                label(x + 22, y + 124, "RANK", size=10, color="#829aaa", weight="700"),
                label(x + 78, y + 124, "FRAMEWORK", size=10, color="#829aaa", weight="700"),
                label(x + card_width - 104, y + 124, "SCORE", size=10, color="#829aaa", weight="700", anchor="end"),
                label(x + card_width - 22, y + 124, "STATUS", size=10, color="#829aaa", weight="700", anchor="end"),
            ])
            for index, row in enumerate(verified):
                row_y = y + 153 + index * 36
                rank_color = "#f0c975" if row["rank"] == 1 else "#8ed8c3"
                pieces.extend([
                    label(x + 22, row_y, str(row["rank"]), size=13, color=rank_color, weight="700"),
                    label(x + 78, row_y, row["framework"], size=12, color="#edf3f5"),
                    label(x + card_width - 104, row_y, score_text(row["value"]), size=12, color="#edf3f5", weight="700", anchor="end"),
                    label(x + card_width - 22, row_y, "verified", size=10, color="#79cdb9", anchor="end"),
                ])
            if not verified:
                pieces.append(label(x + 22, y + 158, "No independently verified rank", size=12, color="#b0bdc6"))

    x, y = positions[-1]
    pieces.extend([
        f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="16" fill="#11283a" stroke="#29465a" stroke-width="1.4"/>',
        label(x + 22, y + 35, "Archive coverage", size=20, color="#f4f0e5", weight="700"),
        label(x + 22, y + 61, "Full leaderboard records", size=12, color="#9eb2c2"),
        f'<line x1="{x + 20}" y1="{y + 83}" x2="{x + card_width - 20}" y2="{y + 83}" stroke="#2a4558"/>',
        label(x + 24, y + 151, str(verified_count), size=43, color="#7ddfc4", weight="700"),
        label(x + 24, y + 177, "verified ranked score cells", size=13, color="#d7e2e7"),
        label(x + 24, y + 230, str(self_reported_count), size=34, color="#f0c975", weight="700"),
        label(x + 24, y + 256, "self-reported scores · unranked", size=13, color="#d7e2e7"),
        label(x + 24, y + 300, "Rank groups match topic, model and protocol.", size=12, color="#9eb2c2"),
    ])

    pieces.extend([
        '<text x="60" y="948" fill="#829aaa" font-family="Arial,sans-serif" font-size="12">Historical scores · displayed to 4 decimal places · full tables and exact values are linked below.</text>',
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
    figure_content = readme_figure_svg(rows, snapshot)
    if args.check:
        if not figure_path.is_file() or figure_path.read_text(encoding="utf-8") != figure_content:
            parser.exit(1, f"stale leaderboard output: {figure_path.relative_to(ROOT)}\n")
    else:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure_path.write_text(figure_content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
