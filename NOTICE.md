# NOTICE

## Derived content

Portions of this repository (task contracts, scorer glue, schemas, and
templates) are derived from the `researchclaweval-public` project, which is
licensed under the Apache License 2.0. Both projects are authored by the same
single copyright holder, who relicenses those portions under the MIT License
(see `LICENSE`) for this repository.

## Documentation license

Documentation in `docs/`, the READMEs, and the contracts are licensed under
the Creative Commons Attribution 4.0 International (CC-BY-4.0). You are free
to share and adapt them with attribution.

## Secrets policy

- The LLM-judge pipeline (`judge/`) reads all credentials exclusively from
  environment variables (`JUDGE_API_KEY` / `JUDGE_MODEL` / `JUDGE_BASE_URL`).
  The source contains no secrets and no default credential values, and the
  release gate (`scripts/check-release.sh`) scans for credential patterns on
  every change.
- Model API configuration is read at run time from `OPENAI_BASE_URL`,
  `OPENAI_API_KEY`, and `OPENAI_MODEL`. The repository does not select a provider;
  users configure their endpoint, API key, and model name locally. No credentials
  are stored in this repository.

## Data

This repository does not redistribute any dataset. Users download and verify
the public datasets with `scripts/setup_datasets.sh`; see `docs/rules.md` §3
and `THIRD_PARTY_NOTICES.md` for source and license information.
