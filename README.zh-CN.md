# ResearchClawEval Arena

ResearchClawEval Arena 为科研 Agent 框架提供统一的任务运行与结果比较方式。仓库包含五项任务、七个框架适配器、任务契约与评分器、本地批量运行器，以及经复核的历史结果。框架在隔离的 Docker 容器中按原生流程运行。运行者自行选择并在本地配置兼容的模型 API。

<p align="center">
  <a href="https://betterrrrr.github.io/researchclaweval-arena/leaderboard/">
    <img src="https://raw.githubusercontent.com/betterrrrr/researchclaweval-arena/1e313591facd7f12bf04e52a9cdf7f81d0dae79f/assets/leaderboard-snapshot.svg" alt="七个框架的六维历史研究过程评分雷达图" width="100%">
  </a>
</p>
<p align="center"><sub>图中展示七个框架的 Judge 历史过程评分。点击图表可查看完整排行榜。</sub></p>

<h2 align="center">各框架六维过程评分</h2>
<p align="center">
  <a href="https://betterrrrr.github.io/researchclaweval-arena/leaderboard/">
    <img src="https://raw.githubusercontent.com/betterrrrr/researchclaweval-arena/main/assets/framework-radar-cards.svg" alt="七个框架各自的六维评分雷达图" width="100%">
  </a>
</p>
<p align="center"><sub>每张图展示一个框架在六个 Judge 维度上的评分，统一采用 0–1 刻度。图表用于描述过程特征，不构成综合排名。点击图表可查看完整排行榜。</sub></p>

[English](README.md) · [比赛规则](docs/rules.md) · [快速开始](docs/participant_quickstart.zh-CN.md) · [全部历史榜单](results/leaderboard.zh-CN.md) · [结果复核方法](results/README.md) · [历史结果网站](website/README.md)

## 适用范围

比赛自测任务为 ARC-WBE-2026、PsyDefDetect 和 TDC-ADMET-Tox。参赛者可用这三项任务检查接入与运行流程，并在本地迭代；自测成绩不计入比赛排名。正式比赛由主办方在其他任务上统一运行和评分。本仓库发布的历史榜单来自论文数据快照，经证据复核后整理，不代表比赛正式排名。

公开版 Arena 当前提供五项可运行任务。每项任务的数据边界、主要指标和运行限制以对应契约为准。

## 任务

| 任务 | 主要指标 | 方向 | 契约 |
|---|---|---:|---|
| ARC-WBE-2026 | 调整后的末层得分 | 越低越好 | [任务契约](contracts/arc_wbe_2026_contract.md) |
| BabyLM-10M | 验证集困惑度 | 越低越好 | [任务契约](contracts/babylm_contract.md) |
| MountainCar-Continuous | 平均奖励 | 越高越好 | [任务契约](contracts/mountaincar_continuous_contract.md) |
| PsyDefDetect | Macro-F1 | 越高越好 | [任务契约](contracts/psydefdetect_contract.md) |
| TDC-ADMET-Tox | Macro-AUROC | 越高越好 | [任务契约](contracts/tdc_admet_tox_contract.md) |

只准备需要使用的数据。下载脚本会按公开哈希校验文件：

```bash
bash scripts/setup_datasets.sh --dataset psydefdetect
```

## 历史榜单

五项任务的历史榜单均已公开。结果按任务、模型和评测协议分组，不将不同分组的成绩合并为总排名。只有符合复核标准的记录才有名次；缺失、未核验和自报成绩会保留状态。BabyLM 当前记录为框架自报分，不参与排名。

| 任务 | 榜单 |
|---|---|
| ARC-WBE-2026 | [查看结果](results/leaderboard.zh-CN.md#arc-wbe-2026) |
| BabyLM-10M | [查看结果](results/leaderboard.zh-CN.md#babylm-10m) |
| MountainCar-Continuous | [查看结果](results/leaderboard.zh-CN.md#mountaincar-continuous) |
| PsyDefDetect | [查看结果](results/leaderboard.zh-CN.md#psydefdetect) |
| TDC-ADMET-Tox | [查看结果](results/leaderboard.zh-CN.md#tdc-admet-tox) |

可下载包含缺失和未核验记录的[完整 CSV](results/leaderboard.csv)，查看[复核证据数据](results/historical-evidence.json)，或阅读[英文完整榜单](results/leaderboard.md)。[结果说明](results/README.md)介绍数据来源、核验标准和历史记录的适用范围。本地运行不会自动进入公开榜单。

## 框架

仓库包含 AI-Researcher、AI-Scientist-v2、ARIS、AutoResearchClaw、DeepScientist、Dr. Claw 和 EvoScientist 的适配器。每个适配器均有对应五项任务的启动命令，共 35 组路由；所有路由在公开端到端验证前均标记为 experimental。运行以下命令可查看状态：

```bash
python3 scripts/arena.py list
```

`experimental` 表示尚未完成公开端到端验证；不支持的路由会明确显示并跳过。各框架要求见[适配器说明](adapters/README.md)。

## 批量运行

安装 Docker 和 Python 3.10 或更新版本。如果框架需要模型 API，请将 [`.env.example`](.env.example) 复制为 `.env`，并在本地配置兼容的服务。仓库不指定服务商，也不包含 API 凭据。

可选择一个任务运行全部内置适配器、选择一个框架运行全部任务，或一次运行完整的 35 组组合：

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
python3 scripts/arena.py run --topic all --framework autoresearchclaw
python3 scripts/arena.py run --topic all --framework all
```

完整矩阵会按顺序运行。使用 `--dry-run` 可在启动 Docker、下载数据或配置 API 前检查所选路由。每批运行会在 `runs/` 下创建独立目录，并在 `summary.json` 中记录各路由状态。框架生成原生执行标记和必需产物后，运行器才会启动本地评分。

## 接入框架

从 [`templates/example-adapter/`](templates/example-adapter/) 开始。在 `adapter.json` 中固定上游代码版本，声明容器镜像和框架原生启动命令，并且只列出能够实际启动的任务。通过 `--adapter ./适配器目录` 运行。适配器格式和检查要求见[快速开始](docs/participant_quickstart.zh-CN.md#添加适配器)。

## 仓库结构

```text
adapters/     内置框架启动配置
configs/      模型服务商配置模板
contracts/    任务输入、输出、数据边界和运行限制
data/         本地下载的数据与缓存（Git 忽略）
docs/         规则、参与者指南、指标说明和常见问题
judge/        过程评测代码和评分标准
results/      经复核的历史榜单、CSV 和证据数据
schemas/      适配器和运行记录的 JSON 格式
scoring/      数据准备和本地评分器
scripts/      数据准备、批量运行和发布检查
splits/       固定任务划分及校验值
templates/    适配器示例和提交产物模板
tests/        运行器、评分器和发布检查
website/      历史论文快照的中英文网站
```

代码采用 MIT 许可，文档采用 CC BY 4.0。第三方许可见[第三方声明](THIRD_PARTY_NOTICES.md)。
