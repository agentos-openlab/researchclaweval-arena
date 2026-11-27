import type { Metadata } from 'next';
import './globals.css';
import {SiteChrome} from '@/components/site-chrome';
export const metadata: Metadata={title:{default:'ResearchClawEval | Research agents, examined',template:'%s | ResearchClawEval'},description:'A research benchmark for outcomes, trajectories, and the process of scientific discovery.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en" translate="no"><body><SiteChrome>{children}</SiteChrome></body></html>}
