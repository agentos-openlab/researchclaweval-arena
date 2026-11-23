# BabyLM-10M

- Task ID: `babylm`
- Dataset: [BabyLM 2026 Strict-Small](https://huggingface.co/datasets/BabyLM-community/BabyLM-2026-Strict-Small), revision `c92ab16b4f08858304b0815706065b3354d8fc0a`
- Dataset path: `/dataset` in the runner. Host setup exports `BABYLM_DATASET_ROOT`.
- Metric: word-level validation perplexity, lower is better.

The framework trains a language model using the six read-only `*.train.txt` files. The input describes the task and constraints. It leaves the hypothesis, model, training procedure, experimental comparisons and selected result to the framework.

## Inputs and split

Prepare the official files with `bash scripts/setup_datasets.sh --dataset babylm`. The command verifies SHA-256 and writes `source_manifest.json` with the source revision and file hashes.

The corpus contains no separate validation set. Create a held-out validation split from these files before training. Record the splitting method, seed, train and validation sizes and preprocessing. Use that same split, tokenizer and preprocessing for every experiment in the run. Word-level perplexity is required for the reported metric.

Perplexities from different validation splits or tokenization protocols are not directly comparable. Archived runs may have used another split. These are Arena validation results and are not submissions to the upstream BabyLM leaderboard.

## Outputs

Under `/workspace`, write `research_idea.json` before the first experiment. Also produce `experiment_trace.json`, `final_report.md`, and the code, configuration and trained artifacts required to reproduce the selected experiment. Identify those artifacts in the trace. Each experiment needs `experiment_id` and a positive finite `validation_perplexity`. `selected_experiment_id` identifies the selected row.

`python3 scoring/run_babylm_local_score.py --workspace <workspace> --output-score <path>` reads the selected trace value. The output is labeled `framework_self_reported` and `rank_eligible: false`. It does not independently evaluate a trained model. Preserve the training artifacts for future independent evaluation.
