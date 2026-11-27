# 快速开始

本指南介绍如何使用内置或自定义适配器运行公开任务。任务输入、输出、运行限制和评分方法见 [`contracts/`](../contracts/)；通用要求见[规则](rules.md)。

## 环境要求

- Python 3.10 或更新版本
- 可运行容器的 Docker Engine
- 首次下载所选数据集和框架源码时可访问网络
- 对需要调用模型 API 的框架，准备一个可用的 API 账户

适配器提供 Dockerfile 时，运行器会从固定的上游提交构建镜像。数据和源码缓存位于 `data/.arena-cache/`。

## 配置模型 API

将 `.env.example` 复制为 `.env`。选择一个支持框架所需 OpenAI 兼容 API 的服务，并在本机填写服务地址、API Key 和可用模型名：

```dotenv
OPENAI_BASE_URL=https://your-provider.example/v1
OPENAI_API_KEY=
OPENAI_MODEL=
```

自测模型由参赛者自行配置，推荐使用 `deepseek-v4.1-flash`，也可选择其他兼容模型。正式评测的模型由主办方统一提供。

`.env` 只保留在本机。不要把密钥写入适配器、命令行参数、报告或提交记录。运行器会遮盖保存日志中的 API Key。部分框架或任务不需要调用模型 API；运行前应查看对应适配器路由和框架要求。

## 查看任务和适配器

```bash
python3 scripts/arena.py list
```

目录会列出五项任务、七个内置适配器及其路由状态。具体模型和平台要求见[适配器说明](../adapters/README.md)。`unsupported` 表示该组合没有启动命令；`experimental` 表示已有启动配置，但尚未完成公开端到端验证。可先用 `--dry-run` 查看组合，无需 Docker、数据或 API 配置：

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all --dry-run
python3 scripts/arena.py run --topic all --framework autoresearchclaw --dry-run
```

## 批量运行

选择一个任务运行所有已声明的内置路由：

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
```

选择一个框架运行全部任务：

```bash
python3 scripts/arena.py run --topic all --framework autoresearchclaw
```

按顺序运行完整的 35 组组合：

```bash
python3 scripts/arena.py run --topic all --framework all
```

运行器只准备所选任务，并在独立容器中逐项执行。未支持的组合会记入批次摘要；只要有组合不支持、运行失败或评分器报错，命令就会以非零状态退出。已完成的运行及本地指标仍保存在批次目录中。需要重跑单项时，明确选择一个任务和一个框架。

每个批次会在 `runs/` 下创建独立目录。记录命令输出的目录路径，并查看其中的 `summary.json`、`logs/e2e.log` 和框架工作区。失败运行的文件不能作为有效成绩。

## 添加适配器

新建目录并在其中添加 `adapter.json`。可从 [`templates/example-adapter/`](../templates/example-adapter/) 开始。自定义清单须声明适配器 ID、名称、任务路由、已有 Docker 镜像、参数数组形式的启动命令，以及由框架本身输出的原生标记。运行器不为自定义适配器构建 Dockerfile。

路由示例：

```json
{
  "image": "my-framework:latest",
  "command": ["python", "/app/run.py", "--input", "/input/prompt.txt"],
  "native_marker": "Framework run started",
  "status": "experimental"
}
```

容器中的 `/input`、`/dataset`、`/arena-adapter` 和 `/arena-scoring` 为只读挂载；`/workspace` 可写且初始为空。环境变量包括 `WORKSPACE`、`DATASET_ROOT`、`ARENA_PROMPT`、`ARENA_TOPIC`，配置后还会传入模型 API 的三个变量。容器不能读取主机仓库或主机数据路径。

使用以下命令试运行自定义适配器：

```bash
python3 scripts/arena.py run --topic <topic-id> --adapter ./path/to/adapter
```

只添加原生流程确实可以启动、且能满足任务契约输出要求的路由。

## 结果说明

运行器先检查框架原生标记和必需文件，再调用评分器。MountainCar 和 ARC-WBE 在无网络隔离容器中评分；ARC 只使用框架可见的验证切分。PsyDefDetect 的标签留在主机侧评分。提供验证集预测文件时，TDC 会计算验证指标。BabyLM 当前读取框架报告的验证困惑度，不会独立重算。

[历史榜单](../results/leaderboard.md)按任务、模型和协议分组，仅展示通过证据核验的名次。本地运行不会自动修改已发布榜单。
