# Benchmark results

The [historical leaderboard](leaderboard.md) reports ranks by task, model and evaluation protocol. The [CSV export](leaderboard.csv) contains the same records, including missing and unverified observations. The [paper snapshot](../website/PAPER-ALIGNMENT.md) is a broader archive from 2026-10-30. Its displayed scores and source-resolution flags do not determine the ranks here.

## Review criteria

The review starts from the selected observations in the paper snapshot. A ranked record must match the archived scorer value and score-file fingerprint. Its original run must have a successful full-run state, a native framework entrypoint and execution marker, and a trace identifying the selected experiment and model. If separate process or outcome records exist, they must pass. The task checks are:

| Task | Evidence required |
|---|---|
| ARC-WBE-2026 | Historical WHEST mini-100 scorer output with no failed MLPs, matching input projection, scoring code and execution budget |
| MountainCar-Continuous | Frozen evaluator and execution budget, with a recorded score from five checkpoints |
| PsyDefDetect | Macro-F1 reproduced from the archived predictions against the public canonical dialogue split, with matching input split and execution budget |
| TDC-ADMET-Tox | Host-side macro-AUROC, matching test and budget fingerprints, and a final audit bound to the prediction file |
| BabyLM-10M | Historical reported perplexity with a score-source fingerprint. Framework-specific and shared-reference protocols are shown separately. Both are unranked. |

A protocol fingerprint identifies compatible task settings for this review. Historical protocols can differ from the current public runner, including ARC's historical 100-MLP scoring set. Two protocol groups are ranked independently even when the task and model match. Rank uses the recorded numeric score in the task's direction and preserves ties. An unverified record remains blank even when the paper archive displays a value. A missing record has no archival score. The reviewed count is a lower bound because the review starts from the archive's selected observation, not all repeat attempts.

## Reproduce the tables

`historical-evidence.json` is the reviewed input. It contains public framework and model labels, protocol and source fingerprints, and the reviewed score or status. Run these commands from the repository root:

```bash
python3 scripts/render_leaderboard.py
python3 scripts/render_leaderboard.py --check
```

To contribute results, follow the framework integration guide and submit the run's task version, model, public configuration, split or evaluator fingerprint, native execution evidence and scoring outputs for review. The leaderboard publishes summarized evidence and omits original logs, credentials, private datasets and internal paths.
