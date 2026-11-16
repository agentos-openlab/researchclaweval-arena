# Leaderboard paper-alignment audit

## Version boundary

The request names the 2026-10-27 paper, but the local build directory retains the 2026-10-30 paper and its generated source, not the requested 2026-10-27 PDF. The explicitly requested 722-pair reliability table and complete five-task main table were integrated on 2026-10-30, as recorded in `../report/judge-v4-integration.md` and `../report/table7-babylm-integration-20261030.md`. They cannot be attributed to the 2026-10-27 version without that document. The site uses the explicitly requested figures as verified against the current local paper and marks the 2026-10-30 data version.

In the current build `build/main.aux`, the requested availability, outcome, and reliability tables appear as Tables 5, 6, and 7, respectively, after renumbering. Figure 3 remains the six-dimensional radar; Tables A4 and A5 remain the process profile and trajectory summaries. Table labels (`6`, `7`, `judge_agreement`, `9`, `8a`) in `generated/english/tables.json` retain their source identities despite displayed renumbering.

## Before this refinement

- All 140 task-score positions, including 15 missing positions, matched the then-current paper-derived table; per-framework counts agreed with the requested availability values.
- All 42 six-dimensional common-condition profile values matched Table A4 and the underlying Figure 3 data. No profile values needed correction.
- Outcome scores were only shown at paper display precision, not the separately archived source precision. Of the 125 retained scores, 96 differ numerically from their displayed rounded value; no discrepancy exceeds the rounding implied by the paper's printed precision. Three shared-reference BabyLM scores also have six-place values in Appendix A2.
- Numerical trajectory summaries, matched-input Judge reliability, a full model matrix, multi-framework radar comparison, and exports were absent. Prior run details identified source roles but did not distinguish execution status from source resolution.

## Automated checks

Run `npm run data:audit` inside the full paper workspace. It compares every matrix cell and paper best marker against the table, checks all three role identities against the frozen source index, checks seven coverage values, checks every radar coordinate against both Table A4 and Figure 3 data, and checks all trajectory, reliability and shared-reference rows. `npm run data:validate` separately checks schema, missing values, availability, best markers, profiles, and reliability coverage.

The 140 cells contain 125 non-null outcomes. Framework availability is 75%, 80%, 100%, 90%, 95%, 95% and 90% in framework order. The shared profile cohort has ten task–model conditions per framework. The trajectory table uses available-record summaries, not that common cohort. The six Judge sample counts total 722 dimension-level matched pairs, not independent runs.

## Data limits

The paper-displayed values remain the values used for paper-best highlighting; archived source values are a separately labeled field. BabyLM has no cross-protocol best markers. Source roles may identify different runs and a resolved source is not proof of execution completion or final artifact identity. Raw score, trace and report files are not linked because public URLs have not been established. CSV and JSON export the current task/model/framework selection, including null results; JSON also retains source evidence fingerprints.
