#!/usr/bin/env python3
"""Download public benchmark inputs from immutable revisions and verify their bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from urllib.request import urlopen

BABYLM_SOURCE = "BabyLM-community/BabyLM-2026-Strict-Small"
BABYLM_REVISION = "c92ab16b4f08858304b0815706065b3354d8fc0a"
BABYLM_FILES = {
    "bnc_spoken.train.txt": "8f3042f4104cf356052fda784682d8e8170fd1fd8c795a1c3e172f9eb2ebfa3c",
    "childes.train.txt": "c898c0a44f4380ce7a66766acd01e70eebbbd9410a1701ddf89452ea6f5aea45",
    "gutenberg.train.txt": "4ddcf5774a7947293ceb56dc76774f553b534231e7ac636c071559229cf2cb9b",
    "open_subtitles.train.txt": "9b21adecf57dd97f611d9442a2f993d2f843278eb24fc98f4165322c1ba5670a",
    "simple_wiki.train.txt": "0ac614aa069ea3908c07c9755bf80bb500d4cee15cd972e9f93cccf89639e9a7",
    "switchboard.train.txt": "89c99649777be2f76f5054e9f1aa364b7e1a62844e219fe810205be6d99399b5",
}
MOUNTAINCAR_SOURCE = "facebookresearch/MLGym"
MOUNTAINCAR_REVISION = "9d40c1b5035202018cd7091fb4e83a9c68b377c0"
MOUNTAINCAR_TASK = "rlMountainCarContinuous"
MOUNTAINCAR_EVALUATOR = "protected/evaluate.py"
MOUNTAINCAR_FILES = {
    "src/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/config.yaml": "c55afc3c1d154100f0e4689bea9ba9cc3d49b2f0b6aebd15beaeb25193d48017",
    "src/helpers.py": "b9e0e07b8020323e892d08ba5ad231d95a2b8c3fcbcf35186bc0a5d8c1099859",
    "src/networks.py": "f7fede2423e2ce084b0b1830aa13b14ccec3e9e440d5892df81dcdefd538ea1e",
    "src/policy.py": "cb07d11550d1e0ccc9393a55df848cb9ac3b814e6612787ccbee1dc9f98bd24b",
    "src/train.py": "c94bf11579d8a2b89af27f891eeb26579878750057fa46cc1daa773108a34a20",
    MOUNTAINCAR_EVALUATOR: "2ccb5436bd2e8ec9974332accceab05d24846baecf1d389e3d922c998f83c50e",
}
ARC_SOURCE = "aicrowd/arc-whestbench-public-2026"
ARC_REVISION = "7c3aa28ba4a6ae6b6d3e4f90f4c35efa12b832f7"
ARC_FILES = {
    "data/mini-00000-of-00003.parquet": "ac706869718024e1cccc74c86a544810e74e6a53028c6ac4e66fdcf5cc799f1a",
    "data/mini-00001-of-00003.parquet": "dedecaa7d90080fe4caade4b7cafe90ff7bc23620a8d8b1bd2bfdd93bafe8023",
    "data/mini-00002-of-00003.parquet": "d11b6d3d81b25bb2a676f587a53f7a71216744352d99824a5832bc1a96a7423e",
}
TDC_ARCHIVE_SHA256 = "bd0005246cb6f1672333c28ad202112a8bf071ab65d847848715030308faf1f1"
TDC_SPLIT_SHA256 = "83bc2a1b6c451adc7da1a31efd550388051abbc9cc912ff9328c9104c17a7ad7"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_verified(urls: list[str], target: Path, expected: str) -> None:
    if target.is_file() and not target.is_symlink() and sha256_file(target) == expected:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    for url in urls:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False) as handle:
            temporary = Path(handle.name)
            try:
                with urlopen(url, timeout=120) as source:
                    shutil.copyfileobj(source, handle)
                handle.close()
                actual = sha256_file(temporary)
                if actual != expected:
                    raise ValueError(f"SHA-256 expected {expected}, got {actual}")
                if os.name == "posix":
                    temporary.chmod(0o644)
                temporary.replace(target)
                return
            except (OSError, ValueError) as exc:
                failures.append(f"{url}: {exc}")
            finally:
                temporary.unlink(missing_ok=True)
    raise RuntimeError(f"could not download and verify {target.name}: " + "; ".join(failures))


def prepare_dataset(topic: str, root: Path) -> None:
    if topic == "mountaincar_continuous":
        repository, revision, files = MOUNTAINCAR_SOURCE, MOUNTAINCAR_REVISION, MOUNTAINCAR_FILES
        base_urls = [f"https://raw.githubusercontent.com/{repository}/{revision}/data/{MOUNTAINCAR_TASK}"]
    else:
        if topic == "babylm":
            repository, revision, files = BABYLM_SOURCE, BABYLM_REVISION, BABYLM_FILES
        elif topic == "arc_wbe_2026":
            repository, revision, files = ARC_SOURCE, ARC_REVISION, ARC_FILES
        else:
            raise ValueError(f"unknown topic: {topic}")
        endpoints = dict.fromkeys(endpoint.rstrip("/") for endpoint in (
            os.environ.get("HF_ENDPOINT", ""), "https://huggingface.co", "https://hf-mirror.com"
        ) if endpoint)
        base_urls = [f"{endpoint}/datasets/{repository}/resolve/{revision}" for endpoint in endpoints]
    for relative_path, digest in files.items():
        upstream_path = "evaluate.py" if relative_path == MOUNTAINCAR_EVALUATOR else relative_path
        urls = [f"{base}/{upstream_path}" for base in base_urls]
        download_verified(urls, root / relative_path, digest)
    manifest = {"topic": topic, "source": repository, "revision": revision, "sha256": files}
    (root / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def verify_derived_dataset(topic: str, root: Path) -> None:
    if topic == "arc_wbe_2026":
        manifest_path = root / "split_manifest.json"
        arc_partitions = {"visible-validation": 10, "scoring": 90}
        names = {
            f"{partition}/data/arc_wbe_2026_{partition}-00000-of-00001.parquet": rows
            for partition, rows in arc_partitions.items()
        }
        provenance = {"topic_id": topic, "seed": 42, "source_total": 100,
                      "visible_count": 10, "scoring_count": 90}
        for partition in arc_partitions:
            path = root / partition / "metadata.json"
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"incomplete ARC split at {root}: missing {path}")
    elif topic == "tdc_admet_tox":
        manifest_path = root / "dataset_manifest.json"
        names = dict.fromkeys(("train.csv", "validation.csv", "test.csv"))
        provenance = {"task_id": topic, "archive_sha256": TDC_ARCHIVE_SHA256,
                      "split_file_sha256": TDC_SPLIT_SHA256}
    else:
        raise ValueError(f"unknown derived dataset: {topic}")
    if manifest_path.is_symlink():
        raise ValueError(f"derived dataset manifest must be a regular file: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or any(manifest.get(key) != value for key, value in provenance.items()):
        raise ValueError(f"derived dataset has wrong source or split: {manifest_path}")
    files = manifest.get("files")
    if not isinstance(files, dict) or files.keys() != names.keys():
        raise ValueError(f"derived dataset manifest has an incomplete file inventory: {manifest_path}")
    for name, rows in names.items():
        path = root / name
        entry = files[name]
        if (
            not isinstance(entry, dict)
            or (rows is not None and entry.get("n_rows") != rows)
            or path.is_symlink() or not path.is_file()
            or sha256_file(path) != entry.get("sha256")
        ):
            raise ValueError(f"derived dataset file failed its integrity check: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    task = parser.add_mutually_exclusive_group(required=True)
    task.add_argument("--topic", choices=("babylm", "mountaincar_continuous", "arc_wbe_2026"))
    task.add_argument("--check-cache", choices=("arc_wbe_2026", "tdc_admet_tox"))
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.check_cache:
            verify_derived_dataset(args.check_cache, args.root)
        else:
            prepare_dataset(args.topic, args.root)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
