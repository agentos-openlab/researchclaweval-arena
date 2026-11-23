"""Exercise the public CLI and its Docker boundary without using a provider."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/arena.py"
spec = importlib.util.spec_from_file_location("arena", CLI)
arena = importlib.util.module_from_spec(spec)
sys.modules["arena"] = arena
spec.loader.exec_module(arena)


class ArenaTests(unittest.TestCase):
    def test_dry_run_expands_only_the_requested_axis(self):
        for flags, count in [
            (["--topic", "psydefdetect", "--framework", "all"], 7),
            (["--topic", "all", "--framework", "autoresearchclaw"], 5),
        ]:
            run = subprocess.run([sys.executable, CLI, "run", *flags, "--dry-run"],
                                 cwd="/tmp", text=True, capture_output=True, check=True)
            jobs = json.loads(run.stdout)
            self.assertEqual(len(jobs), count)
            self.assertEqual(len({(j["topic"], j["framework"]) for j in jobs}), count)

    def test_custom_batch_continues_after_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            calls = []
            def launch(topic, *_args):
                calls.append(topic.id)
                if len(calls) == 1:
                    raise arena.ArenaError("intentional failure")
                return {"status": "completed"}

            with patch.object(arena, "run_pair", side_effect=launch):
                result = arena.run_batch([
                    (arena.TOPICS["psydefdetect"], {"id": "sample"}, {}),
                    (arena.TOPICS["babylm"], {"id": "sample"}, {}),
                ], output, None, {})
            self.assertEqual(calls, ["psydefdetect", "babylm"])
            self.assertEqual([row["status"] for row in result], ["failed", "completed"])
            self.assertEqual(json.loads((output / "summary.json").read_text()), result)

    def test_bad_custom_adapter_is_rejected_before_docker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "adapter.json"
            path.write_text(json.dumps({"id": "custom", "name": "Custom", "topics": {
                "psydefdetect": {"image": "example/custom:latest", "command": "sh -c arbitrary"}
            }}))
            with self.assertRaises(arena.ArenaError):
                arena.load_adapter(path.parent, builtin=False)

    def test_docker_mounts_only_framework_visible_roots_and_no_key_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            command = arena.docker_command("test", {"command": ["python", "run.py"]},
                "arena:test", run / "adapter", run / "workspace", run / "input", run / "visible")
            self.assertIn("--cap-drop", command)
            self.assertIn("OPENAI_API_KEY", command)
            self.assertFalse(any(arg.startswith("OPENAI_API_KEY=") for arg in command))
            self.assertTrue(any("target=/dataset,readonly" in arg for arg in command))
            self.assertTrue(any("target=/workspace" in arg for arg in command))
            self.assertNotIn("/var/run/docker.sock", " ".join(command))

    def test_missing_credentials_fail_before_creating_a_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "runs"
            with patch.dict(arena.os.environ, {}, clear=True):
                with self.assertRaisesRegex(arena.ArenaError, "OPENAI_BASE_URL"):
                    arena.provider_env(None)
            self.assertFalse(run.exists())


if __name__ == "__main__":
    unittest.main()
