# BabyLM-10M Execution Budget

1. Write and lock `research_idea.json` before any experiment. Include the hypothesis, expected failure modes and planned comparison.
2. Complete 2–4 materially distinct experiments. The framework selects the method and its final result. Finish after recording the selected experiment and its artifacts.
3. Use only input files from the current run. Keep the original dataset read-only and record an unchanged validation policy across experiments.
4. Record an experiment identifier and word-level validation perplexity for each complete experiment. Record the selected identifier, the actual model and endpoint, native execution evidence and the final report.
5. Use the injected provider configuration for agent reasoning. Keep credentials and corpus contents out of the report and traces. If an experiment fails or times out, record its actual outcome.
