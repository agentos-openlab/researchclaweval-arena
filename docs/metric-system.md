# Supplementary Metric Definitions

This document describes an optional set of trajectory and report-analysis
metrics. It does not define the primary task scores or the published
historical rankings. The current leaderboard groups records by task, model,
and evaluation protocol; see [`results/leaderboard.md`](../results/leaderboard.md).

The metrics below are currently defined only for the tasks with anchors in
`scoring/metric_anchors.json`. They are not automatically available for all
five topics. Do not infer missing values or use them to combine scores across
tasks.

The community dimensions are `b0 / bT / AUP / UR / ED` and
`PQ / PEA / ER / OU / ECC / SC / CC`.

## 1. Trajectory metrics

The following metrics are calculated from `experiment_trace.json` without
LLM scoring:

| Metric | Definition | Reporting requirement |
|---|---|---|
| `b0` | Anchor-normalized first-experiment score | Use the reference values in §3 |
| `bT` | Anchor-normalized final or selected-experiment score | Use the reference values in §3 |
| `AUP` | Area under experimental progress | Has a `1/N` lower bound; report N and do not average across topics |
| `UR` | Utilization of the permitted experiment budget | Use the task's declared budget |

Missing metric values are recorded as `null`. An anchor score of 0
represents random-level performance and must not substitute for missing
evidence.

## 2. Experiment-design diversity

`ED` evaluates methodological differences between recorded experiments.
It groups experiment descriptions by method, distinguishing repeated
configurations from different approaches. Runs without method descriptions
cannot be evaluated for this dimension; record `null`.

## 3. Normalization anchors

`b0` and `bT` use fixed anchors in `scoring/metric_anchors.json`:

| Topic | Reference at 0 | Reference at 1 | Scale |
|---|---|---|---|
| `tdc_admet_tox` | 0.5, random AUROC | 1.0, perfect AUROC | Linear |
| `psydefdetect` | 0.125, uniform random over 8 positive classes | 1.0, perfect macro-F1 | Linear |
| `arc_wbe_2026` | 0.075, random-level estimator | 1e-06, near-perfect estimator | Logarithmic |

These are calibration references for this supplementary metric set, not
authoritative benchmark baselines. Any report citing them must state this
limitation.

## 4. LLM-judge dimensions

A single judge model evaluates execution artifacts against fixed rubrics:

| Metric | Dimension | Evidence |
|---|---|---|
| `PQ` | Research planning and idea quality | `research_idea.json`, logs |
| `PEA` | Adequacy of experiments for testing the hypothesis | Trace, logs |
| `ER` | Execution robustness | `e2e.log` |
| `OU` | Use of experimental outputs in the report | Report, trace |
| `ECC` | Consistency between evidence and claims | Report, trace, logs |
| `SC` | Consistency of recorded workflow state | Trace |
| `CC` | Completion of the framework's declared obligations | Trace |

The judge model ID is fixed and published for each evaluation period.
Credentials and configuration are read from `JUDGE_API_KEY`, `JUDGE_MODEL`,
and `JUDGE_BASE_URL`; source files contain no credentials or default model ID.
When execution logs conflict with reports or plans, logs take precedence.

### Evaluation limitations

- LLM scoring has additional execution cost and variability. Differences
  below the calibrated tie threshold are reported as ties. Judge dimensions
  do not affect the published task rankings.
- `CC` is relative to obligations inferred from a framework's own run.
  Cross-framework comparison requires a common stage contract; otherwise,
  report `CC` as a descriptive column only.
- For externally supplied runs, the framework operator controls the
  submitted logs. `ER`, `SC`, and `CC` therefore describe the submitted
  evidence and do not establish independently observed execution.

## 5. Comparability and missing values

- Compare raw scores only within the same topic, model, and fixed evaluation
  protocol.
- Do not combine judge scores arithmetically with official task scores.
- Do not average `AUP` across topics; its lower bound depends on N.
- Record missing community metric values as `null`, not 0.
