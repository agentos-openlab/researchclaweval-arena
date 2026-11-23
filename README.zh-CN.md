# ResearchClawEval Arena

ResearchClawEval Arena 是科研 Agent 框架的公开评测基准，提供 5 个任务、7 个框架适配器、本地运行入口和经核验的历史结果。运行者自行配置模型 API；框架在隔离的 Docker 容器中按原生流程执行。

[English](README.md) · [规则](docs/rules.md) · [快速开始](docs/participant_quickstart.zh-CN.md) · [历史榜单](results/README.md) · [历史结果网站](website/README.md)

## 任务

| 任务 | 主要指标 | 评分说明 |
|---|---|---|
| [BabyLM-10M](contracts/babylm_contract.md) | 验证集困惑度 ↓ | 当前为框架自报分；单独展示，独立复核前不参与排名 |
| [MountainCar-Continuous](contracts/mountaincar_continuous_contract.md) | 平均奖励 ↑ | 使用固定版本的 MLGym 评估器，在离线容器中评分 |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | 调整后的末层得分 ↓ | 评分数据与框架输入隔离 |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | Macro-F1 ↑ | 提供给框架的数据不含评测标签 |
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | Macro-AUROC ↑ | 测试标签仅供本地评分器使用 |

下载脚本只准备指定任务，并校验已公布的数据文件：

```bash
bash scripts/setup_datasets.sh --dataset psydefdetect
```

## 框架与排名

仓库包含 AI-Researcher、AI-Scientist-v2、ARIS、AutoResearchClaw、DeepScientist、Dr. Claw 和 EvoScientist 的适配器。运行 `python3 scripts/arena.py list` 可查看每个适配器支持或仍处于实验状态的任务。标记为不支持的组合会明确显示，不会被记作成功运行。

历史榜按任务、模型和评测协议分组。只有通过证据核验的结果才有名次；未核验、缺失以及 BabyLM 自报分均不排名。榜单保留自带论文中的历史记录，和当前运行器产生的新结果分开处理。

查看[榜单和核验方法](results/README.md)，或下载 [CSV](results/leaderboard.csv)。

## 批量运行

安装 Docker 和 Python 3.10 或更新版本。在本地 `.env` 中按 [`.env.example`](.env.example) 配置模型 API，然后查看可用任务：

```bash
python3 scripts/arena.py list
```

选择一个任务运行全部内置适配器，或选择一个框架运行它支持的任务：

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
python3 scripts/arena.py run --topic all --framework autoresearchclaw
```

也可指定包含 `adapter.json` 的自定义适配器目录：

```bash
python3 scripts/arena.py run --topic psydefdetect --adapter ./my-framework
```

需要模型 API 时，请在本机 `.env` 中填写你选择的 OpenAI 兼容服务地址、API Key 和模型名。仓库不指定服务商，也不保存密钥。无需 Docker、数据下载和 API 配置即可用 `--dry-run` 检查所选组合。每批运行会在 `runs/` 下创建独立目录，并在 `summary.json` 中记录成功和失败。只有框架自身输出原生运行标记并生成所需产物后，才会调用本地评分器。

## 添加框架

从 [`templates/example-adapter/`](templates/example-adapter/) 开始。在 `adapter.json` 中固定上游提交，填写镜像和原生启动命令；只声明确实可以启动的任务。API 凭据留在本地环境中，不要提交到仓库。详见[适配器指南](docs/participant_quickstart.zh-CN.md#添加适配器)。

## 仓库结构

```text
adapters/     内置框架启动配置
contracts/    任务输入、输出格式和运行限制
data/         本地数据集和构建缓存（不提交）
docs/         规则、指南、指标定义和常见问题
results/      经核验的历史榜单数据和导出文件
scoring/      数据准备与本地评分器
scripts/      数据准备、批量运行与发布检查
```

代码采用 MIT 许可，文档采用 CC BY 4.0。第三方内容见 [第三方声明](THIRD_PARTY_NOTICES.md)。
