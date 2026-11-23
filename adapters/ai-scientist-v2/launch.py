"""Run the pinned AI Scientist's native ideation and BFTS launchers."""

import os
import runpy
import subprocess
import sys
from pathlib import Path

import yaml


def main():
    framework = Path("/opt/framework")
    workspace = Path(os.environ["WORKSPACE"])
    dataset = Path(os.environ["DATASET_ROOT"])
    model = os.environ["OPENAI_MODEL"]
    # These chat-completions models occur in both upstream allowlists. The
    # native feedback and report workflows may send image inputs.
    if model not in {"gpt-4o-2024-05-13", "gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18"}:
        raise SystemExit(
            "AI-Scientist-v2 requires a vision-capable model shared by its native "
            "LLM and VLM paths. Set OPENAI_MODEL to gpt-4o-2024-05-13, "
            "gpt-4o-2024-08-06, or gpt-4o-mini-2024-07-18."
        )

    task = Path("/input/prompt.txt").read_text(encoding="utf-8")
    workshop = workspace / "workshop.md"
    workshop.write_text(task, encoding="utf-8")
    config = yaml.safe_load((framework / "bfts_config.yaml").read_text(encoding="utf-8"))
    config["report"]["model"] = model
    config["copy_data"] = False
    config["exec"]["timeout"] = 300
    agent = config["agent"]
    for role in ("code", "feedback", "vlm_feedback"):
        agent[role]["model"] = model
    agent["num_workers"] = 1
    agent["search"]["num_drafts"] = 1
    agent["multi_seed_eval"]["num_seeds"] = 1
    agent["stages"] = {stage: 1 for stage in agent["stages"]}
    (workspace / "bfts_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    subprocess.run([
        sys.executable, str(framework / "ai_scientist/perform_ideation_temp_free.py"),
        "--model", model, "--workshop-file", str(workshop), "--max-num-generations", "1",
    ], check=True, cwd=workspace)

    from ai_scientist.treesearch import bfts_utils

    native_edit = bfts_utils.edit_bfts_config_file

    def edit_run_config(config_path, idea_dir, idea_path):
        path = Path(native_edit(config_path, idea_dir, idea_path))
        run_config = yaml.safe_load(path.read_text(encoding="utf-8"))
        # Upstream normally makes an empty directory for template-free tasks.
        # Keep its generated idea and expose the benchmark's read-only data.
        description = path.parent / "task-and-selected-idea.md"
        idea = (path.parent / "idea.md").read_text(encoding="utf-8")
        description.write_text(f"{task}\n\n# Selected AI Scientist idea\n\n{idea}", encoding="utf-8")
        run_config.update({"data_dir": str(dataset), "desc_file": str(description)})
        path.write_text(yaml.safe_dump(run_config), encoding="utf-8")
        return str(path)

    bfts_utils.edit_bfts_config_file = edit_run_config
    launch = framework / "launch_scientist_bfts.py"
    sys.argv = [
        str(launch), "--load_ideas", str(workshop.with_suffix(".json")),
        "--writeup-type", "normal", "--num_cite_rounds", "0", "--skip_review",
        "--model_agg_plots", model, "--model_writeup", model,
        "--model_citation", model, "--model_writeup_small", model, "--model_review", model,
    ]
    os.chdir(workspace)
    runpy.run_path(str(launch), run_name="__main__")


if __name__ == "__main__":
    main()
