import { PageIntro, Notice } from '@/components/shared';
import { Leaderboard } from '@/components/leaderboard';
import { arenaQuickstart } from '@/lib/participation';

export default function Page() {
  return (
    <main className="container page">
      <PageIntro label="01 / RESULTS" title="Leaderboard">
        Explore archived task outcomes, research-process profiles, and the evidence behind this historical study.
      </PageIntro>
      <Notice>
        <strong>Historical validation snapshot · 15 October 2026.</strong> The displayed results follow the locally verified 30 October paper data; the requested 27 October version is not available here for comparison. Configurations were not matched for budget, retries, or versions. Source selections do not establish same-run or final-artifact identity.
      </Notice>
      <div className="arena-entry">
        <div>
          <strong>Run the current benchmark</strong>
          <p>The Arena repository provides five topics, seven framework adapters, and instructions for connecting another framework. New runs are saved locally and do not change this archived leaderboard.</p>
        </div>
        <a className="button secondary" href={arenaQuickstart}>Arena quickstart <span aria-hidden="true">↗</span></a>
      </div>
      <Leaderboard />
    </main>
  );
}
