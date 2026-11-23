# Quickstart

This guide runs the public tasks with a built-in or custom framework adapter. Task-specific inputs, limits, outputs, and scoring details are defined in [`contracts/`](../contracts/). General requirements are in [`rules.md`](rules.md).

## Requirements

- Python 3.10 or later
- Docker Engine with permission to run containers
- Network access for the first download of a selected dataset and framework source
- A model API account for frameworks that make API calls

The runner builds framework images from pinned upstream commits where a Dockerfile is provided. Downloads are cached under `data/.arena-cache/`.

## Configure the model API

Copy `.env.example` to `.env`. Choose a provider that supports the OpenAI-compatible API used by your framework, then enter its endpoint, API key, and an available model name:

```dotenv
OPENAI_BASE_URL=https://your-provider.example/v1
OPENAI_API_KEY=
OPENAI_MODEL=
```

Keep `.env` local. Do not put credentials in adapter files, command-line arguments, reports, or commits. The runner redacts the configured API Key from its saved container log. Some frameworks or topics may not use a model API; check the adapter route and framework requirements first.

## Inspect the catalogue

```bash
python3 scripts/arena.py list
```

The catalogue shows all five topics and seven built-in adapters, including the status of each route. Check [adapter notes](../adapters/README.md) for model and platform requirements. `unsupported` means that adapter has no declared launch command for the topic. `experimental` means a launch configuration exists but has not completed full public verification. A dry run prints the selected routes without requiring Docker, data downloads, or API settings:

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all --dry-run
python3 scripts/arena.py run --topic all --framework autoresearchclaw --dry-run
```

## Run a batch

Run one topic with all declared built-in adapters:

```bash
python3 scripts/arena.py run --topic psydefdetect --framework all
```

Run one framework on all topics:

```bash
python3 scripts/arena.py run --topic all --framework autoresearchclaw
```

Run the complete 35-route matrix sequentially:

```bash
python3 scripts/arena.py run --topic all --framework all
```

The runner prepares only the selected topics, then executes each declared route in a separate container. Unsupported routes appear in the batch summary. The command returns a nonzero status if any route is unsupported, fails, or its local scorer reports an error; completed runs and their local metrics remain in the batch directory. Select a single topic and framework to rerun a specific combination.

Each batch writes a timestamp-independent unique directory under `runs/arena-*`. Record the printed path and inspect its `summary.json`, `logs/e2e.log`, and framework workspace. Do not use a failed run's artifacts as a successful score.

## Add an adapter

Create a directory with an `adapter.json`. Begin with [`templates/example-adapter/`](../templates/example-adapter/) and its README. A custom adapter manifest declares an ID, display name, topic routes, an existing Docker image, an argument-array command, and a native marker emitted by the framework itself. Custom adapters use an existing image; the runner does not build a custom Dockerfile.

Example route:

```json
{
  "image": "my-framework:latest",
  "command": ["python", "/app/run.py", "--input", "/input/prompt.txt"],
  "native_marker": "Framework run started",
  "status": "experimental"
}
```

The container receives read-only mounts at `/input`, `/dataset`, `/arena-adapter`, and `/arena-scoring`; `/workspace` is writable and starts empty. It also receives `WORKSPACE`, `DATASET_ROOT`, `ARENA_PROMPT`, `ARENA_TOPIC`, and, when configured, the three model API variables. Do not assume access to the host repository or host data paths.

Use `python3 scripts/arena.py run --topic <topic-id> --adapter ./path/to/adapter` to test it. Add only topic routes that the native workflow can launch and whose required artifacts meet the linked task contract.

## Results and limitations

The runner checks the framework's native marker and required files before scoring. MountainCar and ARC-WBE evaluation run in isolated containers with no network access; ARC uses only the visible-validation split. PsyDefDetect labels remain on the host while predictions are scored. TDC validation scoring runs when the framework provides validation predictions. BabyLM's diagnostic score is framework-reported and is not independently reproduced.

The [historical leaderboard](../results/leaderboard.md) is grouped by topic, model, and protocol. Only reviewed evidence receives a rank. Local runs do not change the published table automatically.
