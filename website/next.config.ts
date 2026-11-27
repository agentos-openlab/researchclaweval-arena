import type { NextConfig } from 'next';
import { PHASE_DEVELOPMENT_SERVER } from 'next/constants';

export default function config(phase: string): NextConfig {
  const githubPages = process.env.GITHUB_PAGES === 'true';
  return {
    output: 'export',
    trailingSlash: true,
    // GitHub project pages live under /<repository-name>/; Vercel serves at /.
    basePath: githubPages ? '/researchclaweval-arena' : undefined,
    // Development and production builds must not overwrite each other's chunks.
    distDir: phase === PHASE_DEVELOPMENT_SERVER ? '.next-dev' : '.next',
  };
}
