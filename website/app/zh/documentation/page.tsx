import { PageIntro, Notice } from '@/components/shared';
import { arenaQuickstart, arenaRepository } from '@/lib/participation';

export default function ChineseDocumentation() {
  return (
    <main className="container page narrow-page">
      <PageIntro label="05 / 文档" title="历史数据与当前评测。">
        本站保存历史评测数据；当前公开基准和本地运行说明见 ResearchClawEval Arena 仓库。
      </PageIntro>

      <Notice>
        本站展示归档结果。新的 Arena 运行由使用者在本地发起并保存，不会自动更改本站的历史表格或公开榜单。
      </Notice>

      <section className="prose-section">
        <span className="index">01 / 当前基准</span>
        <h2>运行 Arena 任务</h2>
        <p>
          Arena 仓库提供五项任务、七个内置框架适配器、批处理运行器和自定义框架接入说明。可以选择一项任务运行所有适用框架，也可以选择一个框架运行其支持的任务。各框架的任务支持范围和运行状态可通过命令行查看。
        </p>
        <p>
          需要模型 API 时，请自行选择与框架兼容的服务，并在本机配置地址、密钥和模型名。公开仓库不指定服务商，也不保存凭据。
        </p>
        <div className="actions">
          <a className="button primary" href={arenaQuickstart}>查看运行指南 <span aria-hidden="true">↗</span></a>
          <a className="button secondary" href={arenaRepository}>查看代码仓库 <span aria-hidden="true">↗</span></a>
        </div>
      </section>

      <section className="prose-section">
        <span className="index">02 / 历史数据</span>
        <h2>查看归档结果</h2>
        <p>
          本站排行榜展示历史研究中的任务、模型和框架记录，不代表当前 Arena 运行结果。仓库另行维护经证据核验的历史排名；两处数据均保留任务、模型、评价器和评测协议。
        </p>
        <p>
          不应直接合并不同任务的原始分数，也不应比较评测协议不同的 BabyLM 结果。过程画像来自模型评审，不等同于独立专家共识。
        </p>
      </section>

      <section className="prose-section">
        <span className="index">03 / 本地运行网站</span>
        <h2>启动网站</h2>
        <p>在网站目录中安装依赖并启动开发服务器：</p>
        <pre><code>{`npm ci
npm run dev`}</code></pre>
        <p>
          运行 <code>npm run build</code> 可生成静态站点。JSON 数据已包含在站点中，构建不依赖论文工作区。
        </p>
      </section>

      <section className="prose-section">
        <span className="index">04 / 数据结构</span>
        <h2>四份版本化 JSON 数据</h2>
        <div className="doc-table">
          <div><code>runs.json</code><span>任务、模型和框架结果及来源角色。</span></div>
          <div><code>leaderboard.json</code><span>用于页面展示的历史结果和过程画像。</span></div>
          <div><code>tasks.json</code><span>任务输入、交付物、指标方向和验证边界。</span></div>
          <div><code>frameworks.json</code><span>框架标识和架构说明。</span></div>
        </div>
        <p>
          文件记录数据版本、快照日期和来源文件的 SHA-256 指纹。来源记录和哈希用于定位档案材料，不能证明记录来自同一次运行。来源路径和复现限制见网站 README。
        </p>
      </section>

      <section className="prose-section">
        <span className="index">05 / 引用</span>
        <h2>使用正式出版信息</h2>
        <p>论文正式发表后，请采用最终书目信息；本站不预填未经确认的 DOI 或出版日期。</p>
      </section>
    </main>
  );
}
