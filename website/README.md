# ResearchClawEval benchmark website

The bilingual static benchmark website is published with GitHub Pages at:

- English: https://betterrrrr.github.io/researchclaweval-arena/
- 简体中文: https://betterrrrr.github.io/researchclaweval-arena/zh/

The GitHub Actions workflow builds this directory with `GITHUB_PAGES=true`. Next.js exports project-relative routes under `/researchclaweval-arena/`. For local development, run `npm ci` and `npm run dev`. For local builds outside GitHub Pages, run `npm run build` without `GITHUB_PAGES`.

The site presents the 2026-10-15 historical snapshot using the locally verified 2026-10-30 paper data. It does not provide online evaluation or accept result submissions. The Arena self-test tasks are linked separately and do not modify this historical leaderboard.
