# Archived artifact format

This directory documents the artifact layout used by the paper's historical evaluations. It is not used by the current Arena batch runner.

For current runs, use `python3 scripts/arena.py run ...`. Each run is saved under `runs/arena-*`, with a `summary.json`, native framework logs, required task outputs, and local scores where a scorer is available. See the task contracts and [`docs/participant_quickstart.md`](../../docs/participant_quickstart.md).

The files and worked example in this directory remain for validating the historical artifact format. Historical records must preserve their original provenance and scoring evidence.
