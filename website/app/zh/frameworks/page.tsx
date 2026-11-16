import {frameworks,leaderboard} from '@/lib/data';import {PageIntro,Notice} from '@/components/shared';
const descriptions:Record<string,string>={
 '01':'由多个专门智能体协作完成文献分析、方法开发与论文撰写。',
 '02':'通过实验管理器和智能体树搜索组织实验探索。',
 '03':'以可复用技能、跨模型审阅和研究知识库连接研究流程。',
 '04':'采用分阶段的“构想到论文”流程，并在筛选与迭代之间作出决策。',
 '05':'通过多智能体假设检验和持续积累的研究记忆推进研究。',
 '06':'在可由人类引导的研究工作区中编排代码执行器。',
 '07':'由研究员、工程师和进化管理者协作，并保留研究与实验记忆。',
};
export default function ChineseFrameworks(){return <main className="container page"><PageIntro label="04 / 科研框架" title="七种科研组织方式。">从分阶段流程到多智能体协作，基准测试兼容不同的科研工作流。</PageIntro><Notice>框架简介概括论文中记录的架构。评测结果描述历史上的框架—模型配置，不代表框架本身的固有能力。</Notice><div className="framework-grid">{frameworks.map(f=>{const p=leaderboard.profiles.find(p=>p.frameworkId===f.id);return <article key={f.id}><div className="card-top"><span className="index">框架 / {f.id}</span><span>↗</span></div><h2>{f.name}</h2><p>{descriptions[f.id]}</p><div className="card-foot"><span>共同过程评价条件</span><b>{p?.conditions} / 10</b></div></article>})}</div></main>}
