"""Tests for public dataset integrity and the new topic scorers."""

import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scoring"))
import prepare_public_topic_data as prepare
import run_babylm_local_score as babylm
import run_mountaincar_continuous_score as mountaincar


class PublicDataTests(unittest.TestCase):
    def test_reuses_verified_file_and_repairs_corrupt_file(self):
        contents = b"public dataset bytes"
        digest = hashlib.sha256(contents).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "asset"
            with patch.object(prepare, "urlopen", side_effect=lambda *_a, **_kw: io.BytesIO(contents)) as fetch:
                prepare.download_verified(["https://example.org/asset"], target, digest)
                self.assertEqual(target.read_bytes(), contents)
                prepare.download_verified(["https://example.org/asset"], target, digest)
                self.assertEqual(fetch.call_count, 1)
                target.write_bytes(b"corrupted")
                prepare.download_verified(["https://example.org/asset"], target, digest)
                self.assertEqual(target.read_bytes(), contents)
                self.assertEqual(fetch.call_count, 2)

    def test_unverified_download_does_not_replace_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "asset"
            target.write_bytes(b"cached")
            with patch.object(prepare, "urlopen", return_value=io.BytesIO(b"wrong response")):
                with self.assertRaisesRegex(RuntimeError, "SHA-256"):
                    prepare.download_verified(["https://example.org/asset"], target, "0" * 64)
            self.assertEqual(target.read_bytes(), b"cached")
            self.assertEqual(list(target.parent.iterdir()), [target])

    def test_arc_cache_rejects_corrupt_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = {}
            for partition, count in (("visible-validation", 10), ("scoring", 90)):
                path = root / partition / "data" / f"arc_wbe_2026_{partition}-00000-of-00001.parquet"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"prepared data")
                entries[path.relative_to(root).as_posix()] = {"sha256": hashlib.sha256(b"prepared data").hexdigest(), "n_rows": count}
                (path.parent.parent / "metadata.json").write_text("{}", encoding="utf-8")
            (root / "split_manifest.json").write_text(json.dumps({"topic_id": "arc_wbe_2026", "seed": 42,
                "source_total": 100, "visible_count": 10, "scoring_count": 90, "files": entries}), encoding="utf-8")
            prepare.verify_derived_dataset("arc_wbe_2026", root)
            path.write_bytes(b"corrupt bytes")
            with self.assertRaisesRegex(ValueError, "integrity check"):
                prepare.verify_derived_dataset("arc_wbe_2026", root)


class BabyLMTests(unittest.TestCase):
    def test_returns_only_selected_self_reported_perplexity(self):
        score = babylm.diagnostic_score({"selected_experiment_id": "selected", "experiments": [
            {"experiment_id": "other", "validation_perplexity": 1.0},
            {"experiment_id": "selected", "validation_perplexity": 7.5},
        ]})
        self.assertEqual(score["score"], 7.5)
        self.assertEqual(score["score_source"], "framework_self_reported")
        self.assertFalse(score["rank_eligible"])

    def test_rejects_missing_selected_or_non_finite_result(self):
        with self.assertRaisesRegex(ValueError, "selected"):
            babylm.diagnostic_score({"selected_experiment_id": "x", "experiments": []})
        with self.assertRaisesRegex(ValueError, "finite"):
            babylm.diagnostic_score({"selected_experiment_id": "x", "experiments": [
                {"experiment_id": "x", "validation_perplexity": float("inf")},
            ]})


class MountainCarTests(unittest.TestCase):
    def test_isolated_evaluator_mount_and_no_credentials(self):
        with patch.object(mountaincar.os, "sched_getaffinity", return_value={7, 4, 8}, create=True):
            args = mountaincar.evaluator_command(Path("/tmp/payload"), Path("/tmp/evaluate.py"), "runtime:local", "score-test")
        self.assertEqual(args[args.index("--network") + 1], "none")
        self.assertEqual(args[args.index("--cpuset-cpus") + 1], "4,7")
        self.assertIn("OPENBLAS_NUM_THREADS=1", args)
        self.assertIn("--read-only", args)
        self.assertIn("--cap-drop=ALL", args)
        self.assertIn("--security-opt=no-new-privileges", args)
        self.assertTrue(all(mount.endswith(",readonly") for mount in args if mount.startswith("type=bind,")))
        self.assertIn("/evaluator/evaluate.py", args)
        self.assertNotIn("OPENAI_", " ".join(args))

    def test_stages_only_expected_paths_and_refuses_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "original"
            (source / "src").mkdir(parents=True)
            (source / "src" / "models.py").write_text("", encoding="utf-8")
            (source / "config.yaml").write_text("", encoding="utf-8")
            (source / "checkpoints").mkdir()
            for n in range(5):
                (source / "checkpoints" / f"config-{n}.pkl").write_bytes(b"test")
            (source / ".env").write_text("private example", encoding="utf-8")
            staged = root / "staged"
            staged.mkdir()
            mountaincar.stage_payload(source, staged)
            self.assertEqual({x.name for x in staged.iterdir()}, {"config.yaml", "src", "checkpoints"})
            (source / "src" / "link.py").symlink_to(source / ".env")
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                mountaincar.stage_payload(source, staged)

    def test_requires_finite_mean_and_nonnegative_deviation(self):
        self.assertEqual(mountaincar.parse_score('diagnostic\n' + json.dumps({"Reward Mean": -3, "Reward Std": .5})), (-3.0, .5))
        for stdout in ('{"Reward Mean": NaN, "Reward Std": 0}', '{"Reward Mean": 1, "Reward Std": -1}'):
            with self.assertRaisesRegex(ValueError, "metric"):
                mountaincar.parse_score(stdout)


if __name__ == "__main__":
    unittest.main()
