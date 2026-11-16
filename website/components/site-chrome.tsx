'use client';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {useEffect} from 'react';
const pages=[['leaderboard','Leaderboard','排行榜'],['tasks','Tasks','任务'],['methodology','Methodology','方法'],['frameworks','Frameworks','框架'],['documentation','Documentation','文档']];
export function SiteChrome({children}:{children:React.ReactNode}){
 const pathname=usePathname()||'/';const zh=pathname==='/zh'||pathname.startsWith('/zh/');
 const local=(slug:string)=>`${zh?'/zh':''}/${slug}/`.replace('//','/');
 const other=zh?pathname.replace(/^\/zh(?=\/|$)/,'')||'/':`/zh${pathname==='/'?'':pathname}`;
 useEffect(()=>{document.documentElement.lang=zh?'zh-CN':'en'},[zh]);
 return <><header className="site-header"><div className="nav-wrap"><Link href={zh?'/zh/':'/'} className="brand"><span className="brand-mark"><i/><i/><i/><i/></span><span>ResearchClaw<span className="brand-eval">Eval</span></span></Link><nav aria-label={zh?'主导航':'Main navigation'}>{pages.map(([slug,en,cn])=><Link href={local(slug)} key={slug}>{zh?cn:en}</Link>)}</nav><div className="nav-actions"><Link href={local('leaderboard')} className="nav-cta">{zh?'查看结果':'Explore results'} <span>↗</span></Link><Link href={other} className="language-toggle" lang={zh?'en':'zh-CN'} aria-label={zh?'Switch to English':'切换到中文'}>{zh?'EN':'中文'}</Link></div></div></header>{children}<footer><div className="container footer-inner"><div><Link href={zh?'/zh/':'/'} className="footer-brand">ResearchClawEval<span>.</span></Link><p>{zh?'让科研智能体评测更透明。':'Making research-agent evaluation more inspectable.'}</p></div><div className="footer-links">{pages.slice(1,5).map(([slug,en,cn])=><Link href={local(slug)} key={slug}>{zh?cn:en}</Link>)}</div><div className="footer-note">{zh?'历史验证快照':'HISTORICAL VALIDATION SNAPSHOT'}<br/>{zh?'2026年10月15日':'15 OCT 2026'}</div></div></footer></>
}
