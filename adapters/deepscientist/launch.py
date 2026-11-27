"""Start a DeepScientist quest with its built-in OpenCode runner."""

import json
import os
import subprocess
from pathlib import Path


def main():
    workspace = Path(os.environ["WORKSPACE"])
    topic = os.environ["ARENA_TOPIC"]
    model = os.environ["OPENAI_MODEL"]
    config_dir = Path.home() / ".config" / "opencode"
    config_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "provider": {
            "arena": {
                "name": "Arena",
                "npm": "@ai-sdk/openai-compatible",
                "options": {
                    "baseURL": os.environ["OPENAI_BASE_URL"],
                    "apiKey": "{env:OPENAI_API_KEY}",
                },
                "models": {model: {"name": model}},
            },
        },
    }
    (config_dir / "opencode.json").write_text(json.dumps(config), encoding="utf-8")

    # DeepScientist keeps native quest history and Git worktrees under its home.
    home = workspace / "native-artifacts"
    runner = ["ds", "--home", str(home)]
    os.environ.update({
        "GIT_AUTHOR_NAME": "Arena",
        "GIT_AUTHOR_EMAIL": "arena@localhost",
        "GIT_COMMITTER_NAME": "Arena",
        "GIT_COMMITTER_EMAIL": "arena@localhost",
    })
    subprocess.run([*runner, "init"], check=True)
    subprocess.run([*runner, "new", f"Arena benchmark: {topic}", "--quest-id", topic], check=True)
    task = Path("/input/prompt.txt").read_text(encoding="utf-8")
    for stage in ("idea", "baseline", "experiment", "write"):
        message = (
            f"{task}\n\nContinue the native DeepScientist quest at the {stage} stage. "
            "Keep all scientific work within the shared task budget across stages. "
            "Reuse the native quest's earlier results. Complete the required final "
            "artifact handoff to /workspace in the write stage."
        )
        subprocess.run([
            *runner, "run", stage, "--quest-id", topic, "--runner", "opencode",
            "--model", f"arena/{model}", "--message", message,
        ], check=True)


if __name__ == "__main__":
    main()
