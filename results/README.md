# Historical benchmark results

The complete historical tables are available for all five public Arena topics. These rankings reproduce reviewed records from the archived paper snapshot; they are not the official standings of the current competition. The three competition self-test topics and their local scores do not determine the official competition result.

## Browse the rankings

| Topic | Results |
|---|---|
| ARC-WBE-2026 | [Open table](leaderboard.md#arc-wbe-2026) |
| BabyLM-10M | [Open table](leaderboard.md#babylm-10m) |
| MountainCar-Continuous | [Open table](leaderboard.md#mountaincar-continuous) |
| PsyDefDetect | [Open table](leaderboard.md#psydefdetect) |
| TDC-ADMET-Tox | [Open table](leaderboard.md#tdc-admet-tox) |

Read the complete tables in [English](leaderboard.md) or [简体中文](leaderboard.zh-CN.md). Download the [CSV export](leaderboard.csv), which includes ranked, self-reported, unverified, and missing records, or inspect the [reviewed input data](historical-evidence.json). The [paper snapshot](../website/PAPER-ALIGNMENT.md) is a broader archive dated 2026-10-30. Its displayed scores and source-resolution flags do not determine leaderboard ranks.

The current export contains 35 ranked score cells and 13 self-reported score cells. The remaining records are shown with their review status. Each framework's selected archived observation is reviewed; the reviewed run count is therefore a lower bound, not a complete count of all historical attempts.

## Review criteria

The review starts from selected observations in the paper snapshot. A ranked record must match the archived scorer value and score-file fingerprint. Its original run must have a successful full-run state, a native framework entrypoint and execution marker, and a trace identifying the selected experiment and model. If separate process or outcome records exist, they must pass.

| Topic | Evidence required |
|---|---|
| ARC-WBE-2026 | Historical WHEST mini-100 scorer output with no failed MLPs, matching input projection, scoring code, and execution budget |
| MountainCar-Continuous | Frozen evaluator and execution budget, with a recorded score from five checkpoints |
| PsyDefDetect | Macro-F1 reproduced from archived predictions against the public canonical dialogue split, with matching input split and execution budget |
| TDC-ADMET-Tox | Host-side macro-AUROC, matching test and budget fingerprints, and a final audit bound to the prediction file |
| BabyLM-10M | Historical reported perplexity with a score-source fingerprint; framework-specific and shared-reference protocols are listed separately and remain unranked |

A protocol fingerprint identifies compatible task settings for this review. Historical protocols can differ from the current public runner, including ARC's historical 100-MLP scoring set. Groups with different protocols are ranked independently even when task and model match. Ties share a rank, and each task's metric direction determines the order. An unverified record remains unranked even when the paper archive displays a value. A missing record has no archival score.

## Reproduce the tables

`historical-evidence.json` is the reviewed input. It contains public framework and model labels, protocol and source fingerprints, and the reviewed score or status. Run these commands from the repository root:

```bash
python3 scripts/render_leaderboard.py
python3 scripts/render_leaderboard.py --check
```

To submit a new result for review, provide the task version, model, public configuration, split or evaluator fingerprint, native execution evidence, and scoring outputs. The published leaderboard summarizes the evidence and omits original logs, credentials, private datasets, and internal paths. Local runs do not update the tables automatically.
