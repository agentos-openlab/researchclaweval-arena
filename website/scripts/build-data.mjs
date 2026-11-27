import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
const root = new URL('../../', import.meta.url);
const read = p => JSON.parse(readFileSync(new URL(p, root), 'utf8'));
const hash = p => createHash('sha256').update(readFileSync(new URL(p, root))).digest('hex');
const tablePath='generated/english/tables.json';
const indexPath='results/snapshots/server-paper-20261025T105508Z/paper/experiments_20261019/source_provenance.json';
const tables=read(tablePath), index=read(indexPath).rows;
const table = id => tables.find(t=>t.table===id).rows;
const names=['AI-Researcher','AI-Scientist-v2','ARIS','AutoResearchClaw','DeepScientist','DrClaw','EvoScientist'];
const descriptions=['Specialized agents for literature, methods and writing.','Experiment manager with agentic tree search.','Reusable research skills, cross-model review and a research wiki.','A staged idea-to-paper pipeline with screening and refine-or-pivot decisions.','Multi-agent hypothesis testing with cumulative findings memory.','A human-steerable research workspace wrapping coding-agent executors.','Researcher, Engineer and Evolution Manager roles with persistent research memory.'];
const frameworks=names.map((name,i)=>({id:String(i+1).padStart(2,'0'),name,description:descriptions[i]}));
const tasks=[
{id:'arc',name:'ARC-WBE-2026',area:'Scientific computing',metric:'Adjusted final-layer score',direction:'lower',input:'Multilayer perceptron weights',output:'Estimator and submission',boundary:'Predictions must match the required shape; labels remain host-side.',initialization:'Baseline-free'},
{id:'mc',name:'MountainCar-Continuous',area:'Reinforcement learning',metric:'Mean reward',direction:'higher',input:'Environment and PPO starter code',output:'Runnable trained policy',boundary:'Evaluator and policy identity must be recorded.',initialization:'Frozen MLGym PPO starter'},
{id:'babylm',name:'BabyLM-10M',area:'Language modeling',metric:'Validation perplexity',direction:'lower',input:'Strict-Small training text',output:'Trained language model and experiment trace',boundary:'Comparisons require matching validation text, NLL units, denominator and unknown-word treatment.',initialization:'Baseline-free'},
{id:'psydef',name:'PsyDefDetect',area:'Classification',metric:'Macro-F1 (labels 1–8)',direction:'higher',input:'Labeled dialogue inputs',output:'Predictions on the evaluation split',boundary:'Use the intended split and exclude label 0.',initialization:'Baseline-free'},
{id:'tdc',name:'TDC-ADMET-Tox',area:'Molecular prediction',metric:'Mean AUROC (AMES, hERG, DILI)',direction:'higher',input:'Public molecular features',output:'Prediction probabilities for three endpoints',boundary:'Hidden labels remain host-only; public and test roots are separated.',initialization:'Baseline-free'}];
const modelOrder=['GPT-6-Luna','GPT-5.6-Luna','DeepSeek-V4','Kimi-K2.6'];
const matrix=table('7').slice(1);
const runs=[];
for(let ti=0;ti<tasks.length;ti++) for(let fi=0;fi<7;fi++) for(let mi=0;mi<4;mi++){
 const task=tasks[ti],framework=frameworks[fi],model=modelOrder[mi], cell=matrix[ti*7+fi],raw=cell[mi+1].replaceAll('*','');
 const source=index.find(r=>r.framework===framework.id&&r.topic===task.id&&r.model===model);
 if(!source||cell[0]!==framework.name) throw Error('Source mismatch '+[task.id,framework.id,model]);
 const value=raw==='N/A'?null:Number(raw); const paperBest=task.id!=='babylm'&&cell[mi+1].includes('**'); const sourceValue=value===null?null:(source.official?.snapshot_values?.official_final??null); if(value!==null&&!Number.isFinite(value))throw Error('Invalid value');
 const roles=Object.fromEntries(['official','trajectory','judge'].map(role=>[role,{status:source[role]?.status??'unknown',recordId:source[role]?.snapshot_basename||null, evidenceHashes:(source[role]?.sources||[]).flatMap(s=>(s.evidence||[]).filter(e=>e.sha256).map(e=>({kind:e.kind,sha256:e.sha256})))}]));
 runs.push({id:`${framework.id}:${task.id}:${model}`,frameworkId:framework.id,taskId:task.id,model,value,displayValue:raw==='N/A'?null:raw,metric:task.metric,direction:task.direction,paperBest,sourceValue,protocol:task.id==='babylm'&&value!==null?(framework.id==='02'?'shared-reference':'framework-specific'):null,source:roles});
}
const profiles=table('9').slice(1).map(row=>({frameworkId:frameworks.find(f=>f.name===row[0]).id,values:row.slice(1).map(Number),conditions:10}));
const availability=table('6').slice(1,-1).map(row=>({frameworkId:frameworks.find(f=>f.name===row[0]).id,percent:Number(row[1].replace('%',''))}));
const trajectory=table('8a').slice(1).map(row=>({frameworkId:frameworks.find(f=>f.name===row[0]).id,values:row.slice(1).map(Number)}));
const reliability=table('judge_agreement').slice(1).map(row=>{const m=row[3].match(/([0-9.]+) \[([0-9.]+), ([0-9.]+)\]/);if(!m)throw Error('Invalid reliability row');return {dimension:row[0],n:Number(row[1]),exact:Number(row[2]),kappa:Number(m[1]),low:Number(m[2]),high:Number(m[3])}});
const referencePpl=table('7e').slice(1).map(row=>({framework:row[0],model:row[1],value:row[2]}));
const meta={schemaVersion:'1.0.0',snapshot:'2026-10-15',status:'historical validation snapshot',paperDataVersion:'2026-10-30',sourceFiles:[{path:tablePath,sha256:hash(tablePath)},{path:indexPath,sha256:hash(indexPath)}],note:'The four JSON files are derived from frozen local evidence. Source roles can refer to different records; identity and final-artifact bindings are not established by this export.'};
mkdirSync(new URL('../data/',import.meta.url),{recursive:true});
for(const [name,items] of Object.entries({runs,leaderboard:{runs:runs.map(({id,frameworkId,taskId,model,value,displayValue,protocol})=>({id,frameworkId,taskId,model,value,displayValue,protocol})),profiles,availability,trajectory,reliability,referencePpl},tasks,frameworks})) writeFileSync(new URL(`../data/${name}.json`,import.meta.url),JSON.stringify({meta,items},null,2)+'\n');
console.log(`Generated ${runs.length} cells, ${runs.filter(r=>r.value!==null).length} outcomes, ${profiles.length} profiles.`);
