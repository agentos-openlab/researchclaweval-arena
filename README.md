# ResearchClawEval Arena

ResearchClawEval Arena provides a common way to run research-agent frameworks on five research tasks. The repository includes seven framework adapters, task-specific contracts and scorers, a local batch runner, and reviewed historical results. Frameworks run through their native workflows in isolated Docker containers. Users choose and configure a compatible model API locally.

<p align="center">
  <a href="https://betterrrrr.github.io/researchclaweval-arena/leaderboard/">
    <img src="https://raw.githubusercontent.com/betterrrrr/researchclaweval-arena/1e313591facd7f12bf04e52a9cdf7f81d0dae79f/assets/leaderboard-snapshot.svg" alt="Historical six-dimensional research process profiles across seven frameworks" width="100%">
  </a>
</p>
<p align="center"><sub>Historical Judge-coded process profiles across seven frameworks. Click the chart to view the full leaderboard.</sub></p>

<h2 align="center">Framework profiles</h2>
<p align="center">
  <a href="https://betterrrrr.github.io/researchclaweval-arena/leaderboard/">
    <img src="https://raw.githubusercontent.com/betterrrrr/researchclaweval-arena/main/assets/framework-radar-cards.svg" alt="Seven individual six-dimensional radar charts, one per framework" width="100%">
  </a>
</p>
<p align="center"><sub>Each card shows one framework's six Judge-coded scores on the same 0–1 scale. The profiles describe process scores and do not form an overall ranking. Click the charts to view the full leaderboard.</sub></p>

[中文说明](README.zh-CN.md) · [Competition rules](docs/rules.md) · [Quickstart](docs/participant_quickstart.md) · [All benchmark results](results/leaderboard.md) · [Result review method](results/README.md) · [Historical website](website/README.md)

## Scope

The three competition self-test topics are ARC-WBE-2026, PsyDefDetect, and TDC-ADMET-Tox. They let participants check integration and iterate locally; self-test scores do not determine the competition standings. Official competition scoring uses other topics and is run by the organizer. The historical rankings in this repository are reviewed records from a paper snapshot, not the official standings of a competition.

Participants supply their own model for self-testing. We recommend `deepseek-v4.1-flash`, and participants may use any compatible model. The organizer supplies the model for official evaluation.

The public Arena currently provides five runnable topics. Each has its own data boundary, primary metric, and execution limits in its contract.

## Topics

| Topic | Main metric | Direction | Contract |
|---|---|---:|---|
| ARC-WBE-2026 | Adjusted final-layer score | Lower is better | [Contract](contracts/arc_wbe_2026_contract.md) |
| BabyLM-10M | Validation perplexity | Lower is better | [Contract](contracts/babylm_contract.md) |
| MountainCar-Continuous | Mean reward | Higher is better | [Contract](contracts/mountaincar_continuous_contract.md) |
| PsyDefDetect | Macro-F1 | Higher is better | [Contract](contracts/psydefdetect_contract.md) |
| TDC-ADMET-Tox | Macro-AUROC | Higher is better | [Contract](contracts/tdc_admet_tox_contract.md) |

Prepare only the dataset you need. The setup script checks downloaded files against their published hashes:

```bash
bash scripts/setup_datasets.sh --dataset psydefdetect
```

## Historical results

The complete historical tables are public for all five topics. Results are grouped by topic, model, and evaluation protocol; scores from different groups are not combined into an overall ranking. Only records that meet the review criteria receive a rank. Missing, unverified, and self-reported records remain visible with their status. BabyLM values are currently self-reported and are not ranked.

| Topic | Ranking table |
|---|---|
| ARC-WBE-2026 | [View results](results/leaderboard.md#arc-wbe-2026) |
| BabyLM-10M | [View results](results/leaderboard.md#babylm-10m) |
| MountainCar-Continuous | [View results](results/leaderboard.md#mountaincar-continuous) |
| PsyDefDetect | [View results](results/leaderboard.md#psydefdetect) |
| TDC-ADMET-Tox | [View results](results/leaderboard.md#tdc-admet-tox) |

Download the [complete CSV](results/leaderboard.csv), including missing and unverified rows, or inspect the [reviewed evidence data](results/historical-evidence.json). The [review method](results/README.md) explains the source records, verification criteria, and limits of the archive. Local runs do not enter the published tables automatically.

## Frameworks

Seven adapters are included: AI-Researcher, AI-Scientist-v2, ARIS, AutoResearchClaw, DeepScientist, Dr. Claw, and EvoScientist. Each has a launch command for all five topics, for 35 routes total. All routes remain experimental until public end-to-end verification. The catalogue lists their status:

```bash
python3 scripts/arena.py list
```

An `experimental` route has not completed public end-to-end verification. An unsupported route is reported and skipped. See [adapter notes](adapters/README.md) for framework-specific requirements.

## Run a batch

Install Docker and Python 3.10 or later. If a framework needs a model API, copy [`.env.example`](.env.example) to `.env` and configure a compatible provider locally. The repository does not prescribe a provider or include credentials.

Run one topic with all built-in adapters, one framework across all topics, or the complete 35-route matrix:

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
python3 scripts/arena.py run --topic all --framework autoresearchclaw
python3 scripts/arena.py run --topic all --framework all
```

The complete matrix runs sequentially. Use `--dry-run` to inspect the selected routes without Docker, dataset downloads, or API configuration. Each batch writes a separate directory under `runs/` and records route outcomes in `summary.json`. Local scoring starts only after the framework has produced its native execution marker and required artifacts.

## Add a framework

Start with [`templates/example-adapter/`](templates/example-adapter/). Add an `adapter.json` that pins the upstream source, declares the container image and native command, and lists only routes the framework can launch. Run it with `--adapter ./path/to/adapter`. The [quickstart](docs/participant_quickstart.md#add-an-adapter) describes the adapter format and checks.

## Repository layout

```text
adapters/     Built-in framework launch configurations
configs/      Provider configuration template
contracts/    Task inputs, outputs, data boundaries, and execution limits
data/         Local datasets and caches (ignored by Git)
docs/         Rules, participant guides, metric definitions, and FAQ
judge/        Process-evaluation code and rubrics
results/      Reviewed historical tables, CSV, and evidence data
schemas/      JSON formats for adapters and run records
scoring/      Dataset preparation and local scorers
scripts/      Dataset setup, batch runner, and release checks
splits/       Immutable task split manifests and checksums
templates/    Adapter examples and submission artifacts
tests/        Runner, scoring, and release checks
website/      Bilingual site for the archived paper snapshot
```

Code is MIT licensed. Documentation is CC BY 4.0. See [third-party notices](THIRD_PARTY_NOTICES.md).
