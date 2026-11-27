import { PageIntro, Notice } from '@/components/shared';
import { arenaQuickstart, arenaRepository } from '@/lib/participation';

export default function Page() {
  return (
    <main className="container page narrow-page">
      <PageIntro label="05 / DOCUMENTATION" title="Historical results and current runs.">
        This site presents an archived study. The Arena repository contains the current public benchmark and run instructions.
      </PageIntro>

      <Notice>
        The website snapshot and the Arena leaderboard are maintained separately. A local Arena run does not change either published result set.
      </Notice>

      <section className="prose-section">
        <span className="index">01 / CURRENT BENCHMARK</span>
        <h2>Run the Arena topics</h2>
        <p>
          The Arena repository provides five topics, adapters for seven research-agent frameworks, a local batch runner, and instructions for adding another framework. The runner lets you choose one topic across the built-in adapters or one framework across its available topics. It reports unsupported combinations in the run summary.
        </p>
        <p>
          Choose a model API provider that works with your framework and configure its endpoint, API key, and model name locally. The repository does not select a provider. Results are grouped by topic, model, and protocol, and require evidence review before publication.
        </p>
        <div className="actions">
          <a className="button primary" href={arenaQuickstart}>Open the quickstart <span aria-hidden="true">↗</span></a>
          <a className="button secondary" href={arenaRepository}>View the repository <span aria-hidden="true">↗</span></a>
        </div>
      </section>

      <section className="prose-section">
        <span className="index">02 / PAPER SNAPSHOT</span>
        <h2>Read the archived results</h2>
        <p>
          This site preserves the paper snapshot and its task, model, and framework data. Those records describe the archived study and do not represent fresh runs from the current Arena runner. See the Arena repository's reviewed leaderboard for the evidence-qualified historical rankings.
        </p>
        <p>
          Keep the task, model, evaluator, metric direction, and protocol attached to each result. Do not average raw scores across tasks or compare incompatible BabyLM validation protocols.
        </p>
      </section>

      <section className="prose-section">
        <span className="index">03 / WEBSITE DEVELOPMENT</span>
        <h2>Run the website locally</h2>
        <p>From the website directory, install dependencies and start the development server:</p>
        <pre><code>{`npm ci\nnpm run dev`}</code></pre>
        <p>
          Build the static site with <code>npm run build</code>. The generated JSON is included, so the parent paper workspace is not required to build this snapshot.
        </p>
      </section>

      <section className="prose-section">
        <span className="index">04 / DATA CONTRACT</span>
        <h2>Four versioned JSON datasets</h2>
        <div className="doc-table">
          <div><code>runs.json</code><span>Task-model-framework cells, nullable outcomes, and source roles.</span></div>
          <div><code>leaderboard.json</code><span>Display-ready historical results and process profiles.</span></div>
          <div><code>tasks.json</code><span>Task inputs, deliverables, metric directions, and validation boundaries.</span></div>
          <div><code>frameworks.json</code><span>Framework identifiers and architecture descriptions.</span></div>
        </div>
        <p>
          Each file includes a schema version, snapshot date, and SHA-256 fingerprints for its source table and provenance index. See the website README for source paths and reproducibility limits.
        </p>
      </section>

      <section className="prose-section">
        <span className="index">05 / CITATION</span>
        <h2>Use the final publication details</h2>
        <p>
          The manuscript is in preparation. Use its final bibliographic details after publication; this site does not assert a DOI or publication date.
        </p>
      </section>
    </main>
  );
}
