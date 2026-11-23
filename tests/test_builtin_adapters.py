"""Check that the public matrix contains only portable adapter definitions."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {"arc_wbe_2026", "babylm", "mountaincar_continuous", "psydefdetect", "tdc_admet_tox"}
BUILTINS = {"ai-researcher", "ai-scientist-v2", "aris", "autoresearchclaw", "deepscientist", "dr-claw", "evoscientist"}


class BuiltinAdapters(unittest.TestCase):
    def test_builtin_matrix_has_exact_frameworks_and_topics(self):
        manifests = {p.parent.name: p for p in ROOT.glob("adapters/*/adapter.json")}
        self.assertEqual(manifests.keys(), BUILTINS)
        for framework, path in manifests.items():
            with self.subTest(framework=framework):
                manifest = json.loads(path.read_text())
                self.assertEqual(manifest["id"], framework)
                self.assertRegex(manifest["upstream_commit"], r"^[0-9a-f]{40}$")
                self.assertTrue(manifest["native_docs"].startswith("https://github.com/"))
                self.assertEqual(set(manifest["topics"]), TOPICS)
                for topic, route in manifest["topics"].items():
                    with self.subTest(topic=topic):
                        if "reason" in route:
                            self.assertNotIn("command", route)
                            self.assertTrue(route["reason"].strip())
                            continue
                        self.assertIn(route["status"], ("experimental", "verified"))
                        self.assertTrue(route["command"])
                        self.assertTrue(route["native_marker"])
                        if "dockerfile" in route:
                            self.assertTrue((path.parent / route["dockerfile"]).is_file())
                        for value in route["command"]:
                            if value.startswith("/arena-adapter/"):
                                self.assertTrue((path.parent / value.removeprefix("/arena-adapter/")).is_file())
                        serialized = json.dumps(route)
                        self.assertIsNone(re.search(r"(docker\.sock|/home/|--api-key)", serialized))

    def test_first_party_runners_cover_all_topics(self):
        for framework in ("autoresearchclaw", "evoscientist"):
            manifest = json.loads((ROOT / "adapters" / framework / "adapter.json").read_text())
            for topic, route in manifest["topics"].items():
                with self.subTest(framework=framework, topic=topic):
                    self.assertIn("command", route)


if __name__ == "__main__":
    unittest.main()
