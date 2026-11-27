# Third-Party Notices

Framework source code and raw datasets are downloaded from their upstream locations at run time. They are not vendored in this repository. Check the upstream license and usage terms before downloading or running any component.

## Frameworks

The adapters pin each framework to a source commit and record its declared license in `adapters/<id>/adapter.json`.

| Framework | Upstream source | Declared license |
|---|---|---|
| AI-Researcher | [HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) | `NOASSERTION` in adapter metadata; confirm the upstream license before use |
| AI-Scientist-v2 | [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) | `LicenseRef-AI-Scientist-Source-Code-1.0` |
| ARIS | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | MIT |
| AutoResearchClaw | [aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) | MIT |
| DeepScientist | [ResearAI/DeepScientist](https://github.com/ResearAI/DeepScientist) | Apache-2.0 |
| Dr. Claw | [OpenLAIR/dr-claw](https://github.com/OpenLAIR/dr-claw) | `LicenseRef-Combined-GPL-3.0-AGPL-3.0` |
| EvoScientist | [EvoScientist/EvoScientist](https://github.com/EvoScientist/EvoScientist) | Apache-2.0 |

These entries summarize adapter metadata, not legal advice. The source project and its license files control. Some routes are marked `experimental` or `unsupported` in the adapter manifest.

## Datasets

| Asset | Source | Terms |
|---|---|---|
| TDC-ADMET-Tox `admet_group.zip` | [Harvard Dataverse, doi:10.7910/DVN/21LKWG](https://doi.org/10.7910/DVN/21LKWG) | Dataverse terms |
| PsyDefDetect `PsyDefConv.json` | [Hugging Face, AIMH/PsyDefConv](https://huggingface.co/datasets/AIMH/PsyDefConv) | CC BY-NC 4.0; noncommercial use and attribution are required |
| ARC-WBE-2026 | [Hugging Face, aicrowd/arc-whestbench-public-2026](https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026) | CC BY 4.0 |
| BabyLM-2026 Strict-Small | [Hugging Face, BabyLM-community/BabyLM-2026-Strict-Small](https://huggingface.co/datasets/BabyLM-community/BabyLM-2026-Strict-Small) | Follow the dataset card and source-corpus terms |
| MountainCar-Continuous starter and evaluator | [Facebook Research MLGym](https://github.com/facebookresearch/MLGym) | Follow the upstream repository license |

The download and preparation scripts verify the pinned file hashes recorded in the task contracts and `scoring/prepare_public_topic_data.py`. Dataset files remain local and are not uploaded by the batch runner. Model API providers may receive task text sent by a framework; review the provider's terms before use.

## Scoring tools

| Tool | Purpose | License or source |
|---|---|---|
| `whestbench` | ARC-WBE toolkit and evaluator | MIT; see the [upstream repository](https://github.com/AIcrowd/whestbench) |
| `datasets`, `pyarrow` | Dataset access and parquet processing | See package metadata |
| MountainCar evaluator | Local checkpoint evaluation | Pinned source file from MLGym, hash recorded by the setup script |
| `gitleaks` | Release-gate credential scan in CI | MIT; downloaded as a pinned binary |

Third-party libraries used by each framework image retain their upstream licenses. The API endpoint shown in `.env.example` is a service reference only; users supply their own credentials and are responsible for their API account terms.
