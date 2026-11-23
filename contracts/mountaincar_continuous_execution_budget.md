# MountainCar-Continuous Execution Budget

1. Write and lock `research_idea.json` before training. The framework owns the hypothesis, method, experiment design and candidate selection.
2. Run at least one completed experiment. A single training command may run for at most 1,800 seconds. Document the experimental comparisons and selection in `experiment_trace.json`.
3. Advance to artifact finalization once the experiments are complete. Deliver one config, reconstruction code and exactly five trained checkpoints for the selected result. Preserve the original evaluator and evaluation policy.
4. Use the injected provider settings for agent reasoning and record the actual model, endpoint and native execution evidence. Report failures without replacing missing metrics with placeholder values.
