# Custom adapter template

The [`adapter.json`](adapter.json) file is a starter configuration for connecting a research framework to the Arena runner. Replace its ID, name, image, native command, marker, and supported topic routes before running it.

## Configure a route

Each task route contains either:

- `reason`: why this framework does not support the task; or
- `image`, `command`, and `native_marker`: the existing Docker image, its argument-array command, and a distinctive line emitted by the framework's own native workflow.

Set `status` to `experimental` until the route has completed a full end-to-end run and its outputs have been reviewed. Remove unsupported task entries if you do not want to publish a reason for them. The runner uses an existing image for custom adapters; it does not build a custom Dockerfile.

Do not add code to synthesize the framework marker, task outputs, traces, or scores. The adapter starts the framework; the framework owns its research and artifact production.

## Runtime interface

The runner mounts `/input`, `/dataset`, `/arena-adapter`, and `/arena-scoring` read-only. It mounts a fresh, writable run directory at `/workspace`. The container receives `WORKSPACE`, `DATASET_ROOT`, `ARENA_PROMPT`, `ARENA_TOPIC`, and the configured `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` values.

Choose a model API provider that works with your framework and configure it in the local `.env` file, not in this adapter. Never include API keys, private dataset paths, or user-specific endpoints in a manifest.

## Check and run

From the repository root, inspect a route without starting Docker or downloading data:

```bash
python3 scripts/arena.py run \
  --topic psydefdetect --adapter ./my-framework --dry-run
```

Then run it:

```bash
python3 scripts/arena.py run \
  --topic psydefdetect --adapter ./my-framework
```

The runner validates the adapter fields, runs the declared command, checks the native marker and required files, and invokes a local scorer where available. Each task's required outputs and data boundaries are defined in [`contracts/`](../../contracts/).
