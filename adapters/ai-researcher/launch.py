"""Feed an Arena task to AI-Researcher's native reference-based ideation flow."""

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType


def await_server(server, port):
    deadline = time.monotonic() + 10
    while server.poll() is None and time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("AI-Researcher's native execution server did not start")


def run_flow(workspace, topic, task, model, port):
    from research_agent import run_infer_idea as native
    from research_agent.inno.workflow import flowcache

    artifacts = workspace / "native-artifacts"
    artifacts.mkdir()
    instance_path = artifacts / "arena-instance.json"
    instance = {
        "source_papers": [],
        "task_instructions": task,
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "date_limit": time.strftime("%Y-%m-%d", time.gmtime()),
    }
    instance_path.write_text(json.dumps(instance, ensure_ascii=False), encoding="utf-8")

    def arena_instance(instance_path, task_level):
        source = json.loads(Path(instance_path).read_text(encoding="utf-8"))
        return native.EvalMetadata(**source).model_dump()

    native.load_instance = arena_instance
    # Upstream prompts for confirmation before reading a cache. The fresh
    # benchmark workspace can write native traces without interactive retries.
    flowcache.single_select_menu = lambda *_: "No"

    # Native InnoFlow imports the selected category's metaprompt. Map the task
    # contract into that input surface so its own agents author the research.
    module_name = f"benchmark.process.dataset_candidate.{topic}.metaprompt"
    metaprompt = ModuleType(module_name)
    metaprompt.TASK = task
    metaprompt.DATASET = "Use the benchmark input directory at /workspace/arena-dataset."
    metaprompt.BASELINE = "Choose comparison strategies according to the task contract."
    metaprompt.COMPARISON = "Use the prescribed evaluation split for comparisons."
    metaprompt.EVALUATION = task
    metaprompt.REF = ""
    sys.modules[module_name] = metaprompt

    code_env = native.DockerEnv(native.DockerConfig(
        container_name="arena", workplace_name=workspace.name,
        communication_port=port, local_root=str(workspace.parent),
    ))
    file_env = native.RequestsMarkdownBrowser(
        viewport_size=4096, local_root=str(workspace.parent), workplace_name=workspace.name,
        downloads_folder=None,
    )
    flow = native.InnoFlow(
        cache_path=str(artifacts / "cache"), log_path=str(artifacts / "logs"),
        code_env=code_env, file_env=file_env, model=model,
    )

    def with_task(instructions):
        def describe(context):
            native_prompt = instructions(context) if callable(instructions) else instructions
            return (
                f"{native_prompt}\n\nThe following benchmark instructions take precedence over "
                "the generic template's dataset, epoch, GPU, repository and paper requirements. "
                "The preparation agent should inspect the supplied inputs and may select no "
                "external repositories or papers. Use no runtime downloads. Retain the native "
                "workflow and finalize the task's required outputs at /workspace.\n\n"
                f"{task}"
            )
        return describe

    for name in ("prepare_agent", "idea_agent", "code_survey_agent", "coding_plan_agent",
                 "ml_agent", "judge_agent", "exp_analyser"):
        agent = getattr(flow, name).agent
        agent.instructions = with_task(agent.instructions)

    asyncio.run(flow(
        instance_path=str(instance_path), task_level="task_instructions",
        local_root=str(workspace.parent), workplace_name=workspace.name,
        max_iter_times=0, category=topic, references="Use the supplied task contract and dataset.",
    ))


def main():
    workspace = Path(os.environ["WORKSPACE"])
    task = Path("/input/prompt.txt").read_text(encoding="utf-8")
    topic = os.environ["ARENA_TOPIC"]
    # LiteLLM's OpenAI prefix chooses the protocol and is stripped on the wire.
    model = f"openai/{os.environ['OPENAI_MODEL']}"
    os.environ.update({
        "API_BASE_URL": os.environ["OPENAI_BASE_URL"],
        "COMPLETION_MODEL": model,
        "CHEEP_MODEL": model,
        "DOCKER_WORKPLACE_NAME": workspace.name,
        "LOCAL_ROOT": str(workspace.parent),
        "GITHUB_AI_TOKEN": "",
        "EVAL_MODE": "False",
    })
    (workspace / "arena-input").symlink_to("/input", target_is_directory=True)
    (workspace / "arena-dataset").symlink_to(os.environ["DATASET_ROOT"], target_is_directory=True)
    (workspace / "project").mkdir()

    # Reuse the upstream terminal protocol and command server inside the
    # existing Arena container. Bind it to loopback and do not publish a port.
    source = Path("/opt/framework/docker/tcp_server.py").read_text(encoding="utf-8")
    if 'server.bind(("0.0.0.0", args.port))' not in source:
        raise RuntimeError("Unknown AI-Researcher execution-server bind address")
    source = source.replace('server.bind(("0.0.0.0", args.port))',
                            'server.bind(("127.0.0.1", args.port))', 1)
    port = 8000
    with tempfile.TemporaryDirectory(prefix="arena-ai-researcher-") as temp:
        entrypoint = Path(temp) / "tcp_server.py"
        entrypoint.write_text(source, encoding="utf-8")
        server = subprocess.Popen([
            sys.executable, str(entrypoint), "--workplace", str(workspace),
            "--port", str(port),
        ])
        try:
            await_server(server, port)
            run_flow(workspace, topic, task, model, port)
        finally:
            server.terminate()
            server.wait()


if __name__ == "__main__":
    main()
