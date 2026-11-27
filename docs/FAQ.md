# FAQ

[中文](FAQ.zh-CN.md). See [`rules.md`](rules.md) for the complete run and scoring requirements.

## Tasks and runs

**Which topics and frameworks are included?**

There are five topics: BabyLM-10M, MountainCar-Continuous, ARC-WBE-2026, PsyDefDetect, and TDC-ADMET-Tox. Seven built-in framework adapters are listed by `python3 scripts/arena.py list`, together with their route status.

**Can I run all topics and frameworks with one command?**

Yes. All seven built-in adapters declare launch commands for all five topics. Run the complete 35-route matrix sequentially with:

```bash
python3 scripts/arena.py run --topic all --framework all
```

Use `--dry-run` to inspect the selected routes first. Routes remain `experimental` until public end-to-end verification. Unsupported routes in custom adapters are recorded and make the batch exit nonzero.

**Can I connect my own framework?**

Yes. Add an `adapter.json` in a local directory and pass it with `--adapter`. The adapter must launch the framework's native workflow, produce its declared native marker, and meet the task contract. See the [adapter guide](participant_quickstart.md#add-an-adapter).

**What do `experimental` and `unsupported` mean?**

`experimental` means a launch configuration exists but has not completed full public verification. `unsupported` means that no launch command is declared for that task. Neither status represents a verified score.

## API and data

**Which API should I configure?**

Choose a compatible provider for self-testing and enter its endpoint, API key, and model name in a local `.env` file. We recommend `deepseek-v4.1-flash`, and you may choose any compatible model. The organizer supplies the model for official evaluation. Keep credentials local. See the [quickstart](participant_quickstart.md#configure-the-model-api).

**How are datasets prepared?**

Run `bash scripts/setup_datasets.sh --dataset <topic-id>`. The script downloads only the requested task, verifies published file hashes, and stores the data locally under `data/`. The repository does not include the raw datasets.

**Can a framework see evaluation labels?**

No. The runner follows each topic's data boundary. It removes evaluation labels from PsyDefDetect input, separates TDC test labels for host-side scoring, and does not mount ARC's scoring split into the framework container. See each task contract.

**Are BabyLM scores independently checked?**

Not by the current diagnostic scorer. It reads the framework's reported validation perplexity, marks it `framework_self_reported`, and excludes it from ranking until independently reproduced.

## Scores and ranking

**How are results ranked?**

Verified results are ranked within the same topic, model, and evaluation protocol. Raw scores from different tasks or protocols are not combined into an overall total. Ties share a rank.

**Are the published historical rankings the official competition standings?**

No. They reproduce reviewed records from an archived paper snapshot. The three public competition self-test topics are ARC-WBE-2026, PsyDefDetect, and TDC-ADMET-Tox; their self-test scores do not determine the official result. The organizer evaluates the submitted frameworks on other topics. Browse all five historical tables in the [English leaderboard](../results/leaderboard.md) or [Chinese leaderboard](../results/leaderboard.zh-CN.md).

**What does a blank rank mean?**

The result is unverified, missing, or self-reported. Such a record can be displayed with its status, but does not enter ranking. See the [review method](../results/README.md).

**Will a local run appear on the published leaderboard?**

No. New results require evidence review before publication. A local score or model-generated report alone is not sufficient.

**How is ARC-WBE scored?**

The batch runner evaluates the estimator in a network-isolated Docker container against the framework-visible validation split. It does not expose the separate scoring split to the framework.

## Troubleshooting

**What if a batch exits nonzero?**

Open the printed batch directory and inspect `summary.json` and the route's `logs/e2e.log`. A nonzero exit may indicate an unsupported route, missing API configuration, an upstream download or image-build failure, an incomplete native run, or a scoring error. Each run's actual status is retained.

**Where should I report a problem?**

Open a repository issue with the topic, adapter ID, command, summary status, and a minimal reproduction. Remove API Keys, private URLs, and raw dataset rows before sharing logs.
