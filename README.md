# ResearchClawEval Arena

ResearchClawEval Arena is a public benchmark for research-agent frameworks. It contains five runnable topics, adapters for seven frameworks, a local runner, and reviewed historical results. Bring your own model API configuration; runs use the framework's native workflow in an isolated Docker container.

[中文说明](README.zh-CN.md) · [Rules](docs/rules.md) · [Quickstart](docs/participant_quickstart.md) · [Leaderboard](results/README.md) · [Historical website source](website/README.md)

## Topics

| Topic | Main metric | Scoring notes |
|---|---|---|
| [BabyLM-10M](contracts/babylm_contract.md) | Validation perplexity ↓ | Reported by the framework; shown separately and not ranked until independently reproduced |
| [MountainCar-Continuous](contracts/mountaincar_continuous_contract.md) | Mean reward ↑ | Runs the pinned MLGym evaluator in an offline container |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | Adjusted final-layer score ↓ | Scoring data is isolated from the framework |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | Macro-F1 ↑ | Evaluation labels are removed from framework-visible input |
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | Macro-AUROC ↑ | Test labels are available only to the local scorer |

Dataset setup downloads only the selected topic and verifies its published files:

```bash
bash scripts/setup_datasets.sh --dataset psydefdetect
```

## Frameworks and results

The built-in adapters cover AI-Researcher, AI-Scientist-v2, ARIS, AutoResearchClaw, DeepScientist, Dr. Claw, and EvoScientist. Run `python3 scripts/arena.py list` to see the supported and experimental topic routes for each adapter. Routes marked unsupported are reported and skipped; the runner does not claim that every framework supports every task. See [adapter notes](adapters/README.md) for route-specific requirements.

The historical leaderboard groups results by topic, model, and evaluation protocol. A rank is shown only for reviewed results that meet the published evidence criteria. Unverified, missing, and BabyLM self-reported values are not ranked. These records preserve the archived paper results and are distinct from new runs made with the current runner.

See the [rankings and review method](results/README.md), or download the [CSV](results/leaderboard.csv).

## Run a batch

Install Docker and Python 3.10 or later. Configure a model API in a local `.env` file using [`.env.example`](.env.example), then inspect available routes:

```bash
python3 scripts/arena.py list
```

Run one topic with all built-in adapters, or one framework across its available topics:

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
python3 scripts/arena.py run --topic all --framework autoresearchclaw
```

To use your own adapter, provide a directory containing `adapter.json`:

```bash
python3 scripts/arena.py run --topic psydefdetect --adapter ./my-framework
```

Use `--dry-run` to inspect the selected routes without Docker, dataset downloads, or API configuration. The runner creates a fresh batch directory under `runs/`; it records successes and failures in `summary.json`. Each framework run must produce its own native execution marker and required artifacts before local scoring is attempted.

## Add a framework

Start from [`templates/example-adapter/`](templates/example-adapter/). Pin the upstream source to a commit, declare the Docker image and native command in `adapter.json`, and add routes only for topics the framework can actually launch. Keep API credentials in the local environment; do not commit them. See the [adapter guide](docs/participant_quickstart.md#add-an-adapter).

## Repository layout

```text
adapters/     Built-in framework launch configurations
contracts/    Task inputs, output formats, and execution limits
data/         Locally downloaded datasets and build caches (not committed)
docs/         Rules, guides, metric definitions, and FAQ
results/      Reviewed historical ranking data and exports
scoring/      Dataset preparation and local scorers
scripts/      Topic setup, batch runner, and release checks
```

Code is MIT licensed. Documentation is CC BY 4.0. See [third-party notices](THIRD_PARTY_NOTICES.md).
