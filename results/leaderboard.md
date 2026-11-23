# Historical benchmark leaderboard

Paper snapshot: 2026-10-30. Reviewed score cells: 35 ranked and 13 self-reported.

Rankings compare frameworks within a task, model and evaluation protocol. Ties share a rank. The review covers selected paper observations, so the reviewed run count is a lower bound. A blank score denotes a missing or unverified observation. The [review method](README.md) describes the acceptance criteria.

[Download CSV](leaderboard.csv) · [Paper snapshot data](../website/data/runs.json)

## ARC-WBE-2026

Adjusted final-layer score (lower is better).

### DeepSeek-V4 · WHEST historical mini-100 / cff832e85bf1

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | DeepScientist | 0.000214 | verified |
| 2 | EvoScientist | 0.0661 | verified |
| 3 | AutoResearchClaw | 0.27 | verified |
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | Dr. Claw | — | unverified |

### GPT-5.6-Luna · WHEST historical mini-100 / cff832e85bf1

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | Dr. Claw | 0.0909 | verified |
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | EvoScientist | — | unverified |

### GPT-6-Luna · WHEST historical mini-100 / cff832e85bf1

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 9.48e-05 | verified |
| 2 | EvoScientist | 0.0661 | verified |
| 3 | DeepScientist | 0.0761 | verified |
| 4 | Dr. Claw | 0.0852 | verified |
| 5 | AutoResearchClaw | 0.0882 | verified |
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |

### Kimi-K2.6 · WHEST historical mini-100 / cff832e85bf1

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | DeepScientist | 0.0661 | verified |
| 2 | Dr. Claw | 0.0662 | verified |
| 3 | ARIS | 0.0665 | verified |
| — | AI-Researcher | — | missing |
| — | AI-Scientist-v2 | — | missing |
| — | AutoResearchClaw | — | unverified |
| — | EvoScientist | — | unverified |

## BabyLM-10M

Validation perplexity (lower is better).

Framework-reported perplexity is shown for reference. The shared-reference and framework-specific protocols are listed separately.

### DeepSeek-V4 · Framework-specific validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | 106.57618186635331 | self reported |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | 597.4640994670493 | self reported |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |

### DeepSeek-V4 · Protocol not recorded

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | EvoScientist | — | missing |

### DeepSeek-V4 · Shared-reference validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Scientist-v2 | 85.2782377186871 | self reported |

### GPT-5.6-Luna · Framework-specific validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | 742.9706871824764 | self reported |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | 21.579719639362395 | self reported |
| — | DeepScientist | — | unverified |

### GPT-5.6-Luna · Protocol not recorded

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | Dr. Claw | — | missing |
| — | EvoScientist | — | missing |

### GPT-5.6-Luna · Shared-reference validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Scientist-v2 | 108.10571361041116 | self reported |

### GPT-6-Luna · Framework-specific validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | 577.2414134696867 | self reported |
| — | ARIS | 992.2312684364555 | self reported |
| — | AutoResearchClaw | 418.734285402003 | self reported |
| — | DeepScientist | 236.11229910913724 | self reported |
| — | Dr. Claw | 219.19663306523273 | self reported |
| — | EvoScientist | 3021.987278194702 | self reported |

### GPT-6-Luna · Shared-reference validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Scientist-v2 | 185.75492216669167 | self reported |

### Kimi-K2.6 · Framework-specific validation

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

### Kimi-K2.6 · Protocol not recorded

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | missing |
| — | AI-Scientist-v2 | — | missing |
| — | DeepScientist | — | missing |

## MountainCar-Continuous

Mean reward (higher is better).

### DeepSeek-V4 · MLGym frozen evaluator

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | missing |
| — | AutoResearchClaw | — | unverified |

### DeepSeek-V4 · MLGym frozen evaluator / 57ae36653ea7

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 93.67655944824219 | verified |

### DeepSeek-V4 · MLGym frozen evaluator / cbd09e27273b

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | Dr. Claw | 56.47181701660156 | verified |
| 2 | EvoScientist | 52.438758850097656 | verified |
| 3 | DeepScientist | -0.010527188889682293 | verified |

### GPT-5.6-Luna · MLGym frozen evaluator / 57ae36653ea7

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | EvoScientist | 72.51118469238281 | verified |
| 2 | Dr. Claw | -13.969474792480469 | verified |
| — | AI-Researcher | — | missing |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |

### GPT-6-Luna · MLGym frozen evaluator

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

### Kimi-K2.6 · MLGym frozen evaluator

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | missing |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | missing |

### Kimi-K2.6 · MLGym frozen evaluator / 57ae36653ea7

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | Dr. Claw | 74.6320571899414 | verified |
| 2 | DeepScientist | -10.605130195617676 | verified |

### Kimi-K2.6 · MLGym frozen evaluator / cbd09e27273b

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | EvoScientist | 62.6725959777832 | verified |

## PsyDefDetect

Macro-F1 over classes 1–8 (higher is better).

### DeepSeek-V4 · Canonical dialogue split

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | missing |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

### GPT-5.6-Luna · Canonical dialogue split / fa0d1b4e0521

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 0.19041278186114408 | verified |
| 2 | AI-Researcher | 0.13932971957883322 | verified |
| 3 | Dr. Claw | 0.13675435881151377 | verified |
| 4 | DeepScientist | 0.12605264989386505 | verified |
| — | AI-Scientist-v2 | — | unverified |
| — | AutoResearchClaw | — | missing |
| — | EvoScientist | — | unverified |

### GPT-6-Luna · Canonical dialogue split / fa0d1b4e0521

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 0.20000299395120366 | verified |
| 2 | Dr. Claw | 0.13680555555555554 | verified |
| 3 | AI-Researcher | 0.1293855062520251 | verified |
| 4 | EvoScientist | 0.1066673683102668 | verified |
| — | AI-Scientist-v2 | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |

### Kimi-K2.6 · Canonical dialogue split / fa0d1b4e0521

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 0.18736871737061453 | verified |
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

## TDC-ADMET-Tox

Macro-AUROC (higher is better).

### DeepSeek-V4 · Frozen held-out test

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

### GPT-5.6-Luna · Frozen held-out test / 7c8830e94d6c

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | ARIS | 0.822022242699155 | verified |
| 2 | Dr. Claw | 0.8038893754802926 | verified |
| — | AI-Researcher | — | unverified |
| — | AI-Scientist-v2 | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | EvoScientist | — | unverified |

### GPT-6-Luna · Frozen held-out test / 7c8830e94d6c

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | AI-Researcher | 0.8212521416112334 | verified |
| 2 | ARIS | 0.7849937976862559 | verified |
| — | AI-Scientist-v2 | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | Dr. Claw | — | unverified |
| — | EvoScientist | — | unverified |

### Kimi-K2.6 · Frozen held-out test / 7c8830e94d6c

| Rank | Framework | Score | Status |
|---:|---|---:|---|
| 1 | Dr. Claw | 0.7765472892092098 | verified |
| — | AI-Researcher | — | missing |
| — | AI-Scientist-v2 | — | unverified |
| — | ARIS | — | unverified |
| — | AutoResearchClaw | — | unverified |
| — | DeepScientist | — | unverified |
| — | EvoScientist | — | unverified |
