# MountainCar-Continuous

- Task ID: `mountaincar_continuous`
- Upstream: [MLGym `rlMountainCarContinuous`](https://github.com/facebookresearch/MLGym/tree/9d40c1b5035202018cd7091fb4e83a9c68b377c0/data/rlMountainCarContinuous), commit `9d40c1b5035202018cd7091fb4e83a9c68b377c0`
- Environment: `MountainCarContinuous-v0`
- Primary metric: `Reward Mean`, higher is better. Secondary metric: `Reward Std`.

The framework must choose its own experiments for improving the average reward of the continuous-control agent. Compare completed experiments and select one candidate before handing off the artifacts for scoring.

## Inputs

Prepare the public starter files and frozen evaluator with `bash scripts/setup_datasets.sh --dataset mountaincar_continuous`. The host root is `MOUNTAINCAR_CONTINUOUS_DATASET_ROOT`. The runner mounts only its `src/` directory as read-only `/dataset`. Copy the starter files into the run workspace before training. The scorer uses the original SHA-256-verified `protected/evaluate.py` from the host root. The evaluator is not a training input.

## Outputs

Under `/workspace`, produce `research_idea.json`, `experiment_trace.json`, `final_report.md`, `config.yaml`, `src/` with the model reconstruction code, and exactly five trained checkpoints under `checkpoints/` with names matching `config*.pkl`. Keep the model factory and `Model` class compatible with the pinned evaluator. Write and lock the research idea before the first experiment, and identify the selected experiment in the trace.

After finalizing the artifacts, run the evaluator from the host:

```bash
python3 scoring/run_mountaincar_continuous_score.py \
  --workspace <workspace> \
  --dataset-root <dataset-root> \
  --output-score <path>
```

The evaluator tests seeds 0 through 4, with 256 environments per batch and a 200-frame cap. The scoring command stages only `src/`, `config.yaml` and the five checkpoints. It executes the evaluator and submitted model code in a separate Docker container with no network, a read-only root filesystem and no credentials. It reports a local reproduction result. Public ranking admission still requires a review of the run and artifacts.

## Execution Budget

1. Write and lock `research_idea.json` before training. The framework owns the hypothesis, method, experiment design and candidate selection.
2. Run at least one completed experiment. A single training command may run for at most 1,800 seconds. Document the experimental comparisons and selection in `experiment_trace.json`.
3. Advance to artifact finalization once the experiments are complete. Deliver one config, reconstruction code and exactly five trained checkpoints for the selected result. Preserve the original evaluator and evaluation policy.
4. Use the injected provider settings for agent reasoning and record the actual model, endpoint and native execution evidence. Report failures without replacing missing metrics with placeholder values.
