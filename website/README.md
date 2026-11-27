# ResearchClawEval historical-results website

The bilingual static benchmark website is published with GitHub Pages at:

- English: https://betterrrrr.github.io/researchclaweval-arena/
- 简体中文: https://betterrrrr.github.io/researchclaweval-arena/zh/

The GitHub Actions workflow builds this directory with `GITHUB_PAGES=true`. Next.js exports project-relative routes under `/researchclaweval-arena/`. For local development, run `npm ci` and `npm run dev`. For local builds outside GitHub Pages, run `npm run build` without `GITHUB_PAGES`.

The site preserves an archived paper snapshot. It is separate from the current public Arena benchmark, which provides five topics, seven built-in framework adapters, a local batch runner, and evidence-reviewed results grouped by task, model, and protocol. Local runs do not modify this website's snapshot or enter the repository leaderboard automatically.
