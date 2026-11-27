# Contributing

Contributions may add or improve task contracts, framework adapters, scoring tools, data preparation, and documentation. Open a pull request against `main` with a short description of the change and the checks performed.

## Repository requirements

- Do not commit API credentials, raw datasets, private endpoints, local machine paths, or unreviewed run artifacts.
- Add every new tracked file to `scripts/allowlist.txt`. The release gate checks both for unlisted files and stale allowlist entries.
- Keep each task's contract authoritative for its input boundary, metric, outputs, and runtime limits.
- Keep the Chinese rules and quickstart consistent with their English counterparts where both are provided.
- Declare adapter routes only when a framework has a native command for that task. Mark unverified launch configurations `experimental`.
- Include upstream source and license details for framework code and data.

## Local review

The pull request workflow runs the release gate and repository checks. Contributors should review the relevant task path, confirm that new manifests and references are valid, and read the generated diff before opening a pull request. The ARC scorer runs submitted Python code and must only be used in an isolated environment.

The project uses Python's standard library for the Arena runner and most local scorers. Use `uv` for Python environment work and `ruff` for linting and formatting. The MountainCar evaluator uses Docker; ARC tooling requires the packages listed in `scoring/requirements.txt`.

## Licensing

Contributed code is licensed under MIT and documentation under CC BY 4.0, subject to the repository notices and applicable upstream licenses.
