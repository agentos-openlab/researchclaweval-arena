import { PageIntro, Notice } from '@/components/shared';
import { ChineseLeaderboard } from '@/components/leaderboard-zh';
import { arenaQuickstart } from '@/lib/participation';

export default function ChineseLeaderboardPage() {
  return (
    <main className="container page">
      <PageIntro label="01 / 评测结果" title="历史排行榜">
        查看归档研究中的任务结果、科研过程画像，以及相关证据。
      </PageIntro>
      <Notice>
        <strong>历史验证快照 · 2026年10月15日。</strong> 当前展示数值依据本地核验的 10 月 30 日论文数据；本地没有 10 月 27 日版本可供比对。实验配置的预算、重试和版本并未统一。来源解析不能证明记录来自同一次运行或最终产物。
      </Notice>
      <div className="arena-entry">
        <div>
          <strong>运行当前公开基准</strong>
          <p>Arena 仓库提供五项任务、七个框架适配器和自定义框架接入说明。新运行结果保存在本地，不会更改此处的历史排行榜。</p>
        </div>
        <a className="button secondary" href={arenaQuickstart}>查看运行指南 <span aria-hidden="true">↗</span></a>
      </div>
      <ChineseLeaderboard />
    </main>
  );
}
