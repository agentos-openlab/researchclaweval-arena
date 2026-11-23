# Scoring Interfaces

This document summarizes the local scoring tools for all five topics. Task contracts define the authoritative input boundary, metric, output format, and score meaning.

The batch runner calls local scoring after validating a framework's native marker and outputs. It scores BabyLM, MountainCar-Continuous, ARC visible-validation predictions, PsyDefDetect, and TDC validation predictions when present. The historical leaderboard has separate evidence requirements; local outputs do not enter it automatically.

## Dependencies

The main Arena runner and PsyDefDetect/TDC scoring use Python's standard library. Dataset preparation may use `uv`. MountainCar evaluation requires Docker and builds the pinned local image in `scoring/mountaincar_continuous.Dockerfile`. ARC tools require `whestbench`, `datasets`, and `pyarrow` as listed in `scoring/requirements.txt`.

## BabyLM-10M

`scoring/run_babylm_local_score.py` reads the selected experiment's `validation_perplexity` from `experiment_trace.json`. It writes a diagnostic score with `score_source: "framework_self_reported"` and `rank_eligible: false`. It does not load or evaluate the language model. Validation split, tokenizer, and preprocessing must be recorded by the framework; values with different protocols are not comparable.

```bash
python3 scoring/run_babylm_local_score.py \
  --workspace <workspace> --output-score <output.json>
```

## MountainCar-Continuous

`scoring/run_mountaincar_continuous_score.py` stages `config.yaml`, reconstruction code, and exactly five `checkpoints/config*.pkl` files. It runs the SHA-256-verified upstream evaluator in Docker with no network, a read-only root filesystem, no credentials, and a read-only submission mount. It reports mean reward and standard deviation for seeds 0–4.

```bash
python3 scoring/run_mountaincar_continuous_score.py \
  --workspace <workspace> --dataset-root <dataset-root> \
  --output-score <output.json>
```

The result records `scope: "local_reproduction"`, evaluator revision, and hash. It is not a paper rank unless the run also passes the historical evidence review.

## ARC-WBE-2026: `adjusted_final_layer_score`

Lower values are better. The batch runner uses `scoring/run_arc_wbe_2026_local_score.py` to evaluate the estimator against the framework-visible validation split. The tool runs submitted Python in a read-only, network-isolated Docker container with only the scorer code, workspace, visible dataset, and a dedicated output directory mounted. The separate scoring split is not mounted.

```bash
python3 scoring/run_arc_wbe_2026_local_score.py \
  --workspace <workspace> --dataset-root <dataset-root> \
  --output-score <output.json>
```

`scoring/arc_wbe_2026_official_adapter.py` checks the estimator interface and rejects invalid shapes, non-finite, constant, or placeholder predictions. The expected output has shape `(32, 256)`. The framework may read the visible-validation subset; it must not receive the separate scoring labels.

## PsyDefDetect: macro-F1 over labels 1–8

Class 0 is excluded from the primary metric. The scorer compares the framework's predictions with the canonical dialogue split. The host retains the labeled source; the runtime projects evaluation rows without their labels before mounting data into the framework container.

```bash
python3 scoring/run_psydefdetect_local_score.py \
  --dataset-root <labeled-source> --predictions <predictions.jsonl> \
  --output-score <output.json>
```

PsyDefConv is licensed `CC-BY-NC-4.0`; comply with its noncommercial terms and attribution requirements.

## TDC-ADMET-Tox: macro-average AUROC

The primary score is the equal-weight mean AUROC across AMES, hERG, and DILI. The validation scorer supports development and writes diagnostic metrics. The separate test scorer reads public predictions and locally held test labels; those labels are not mounted into framework containers.

```bash
python3 scoring/run_tdc_admet_tox_validation_score.py \
  --validation <validation.csv> --predictions <validation-predictions.csv> \
  --output-metrics <metrics.json>
```

The labeled test scorer is `scoring/run_tdc_admet_tox_host_score.py`. Its arguments and data isolation requirements are documented in [`contracts/tdc_admet_tox_contract.md`](../contracts/tdc_admet_tox_contract.md). Scores on the test set must be tied to the prediction file and the verified dataset split.

## Shared requirements

- Use each task's fixed dataset version and split.
- Keep scoring labels outside framework-visible mounts.
- Preserve framework outputs and actual failure statuses. Do not create substitute score files or copy a score from another run.
- Retain metric direction and protocol with every result. Rank comparisons require the same task, model, and protocol.
- Do not publish credentials, raw private data, or local absolute paths with a result.
