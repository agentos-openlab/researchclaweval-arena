# ResearchClawEval Arena 基准说明

ResearchClawEval Arena 提供科研 Agent 框架的公开运行与结果比较工具。当前版本包含五项任务、七个内置框架适配器、自定义框架接入方式，以及按任务、模型和评测协议整理的历史榜单。

比赛自测任务为 ARC-WBE-2026、PsyDefDetect 和 TDC-ADMET-Tox，参赛者可用这些任务检查框架接入与本地运行。自测分数不计入比赛排名；正式评测由主办方在其他任务上统一运行。仓库中的历史榜单来自论文数据快照，经证据复核后整理，不代表比赛正式成绩。

## 任务

| 任务 | 主要指标 | 说明 |
|---|---|---|
| [BabyLM-10M](../contracts/babylm_contract.md) | 验证集困惑度，越低越好 | 当前为框架自报分，独立复核前不排名 |
| [MountainCar-Continuous](../contracts/mountaincar_continuous_contract.md) | 平均奖励，越高越好 | 使用固定版本评估器复现五个检查点 |
| [ARC-WBE-2026](../contracts/arc_wbe_2026_contract.md) | 调整后的末层得分，越低越好 | 输入数据与评分数据分离 |
| [PsyDefDetect](../contracts/psydefdetect_contract.md) | Macro-F1，越高越好 | 评测标签不提供给框架 |
| [TDC-ADMET-Tox](../contracts/tdc_admet_tox_contract.md) | Macro-AUROC，越高越好 | 测试标签仅供本地评分器使用 |

使用脚本准备单项数据。脚本只下载所选任务并验证固定文件：

```bash
bash scripts/setup_datasets.sh --dataset psydefdetect
```

数据来源、版本、切分、输出格式及运行预算见各任务契约。

## 框架与 API

内置适配器涵盖 AI-Researcher、AI-Scientist-v2、ARIS、AutoResearchClaw、DeepScientist、Dr. Claw 和 EvoScientist。不同框架支持的任务组合不同，可用以下命令查看：

```bash
python3 scripts/arena.py list
```

需要模型 API 时，使用者自行选择与框架兼容的服务，并在本机配置服务地址、API Key 和模型名。公开仓库不指定服务商，也不保存凭据。自定义框架可通过 `adapter.json` 接入；相关要求见[快速开始](participant_quickstart.zh-CN.md)。

## 排名

[五项任务的完整历史榜单](../results/leaderboard.zh-CN.md)复核已发布论文中的评分记录，也可下载[完整 CSV](../results/leaderboard.csv)。结果按任务、模型和评测协议分组；只有来源和评分证据通过核验的记录才参与排序。未核验、缺失和自报记录保留状态，不获得名次。不同任务的原始分不合并为总分。

当前本地运行结果不会自动发布。发布新记录前须经过证据复核，标准和榜单生成命令见 [`results/README.md`](../results/README.md)。
