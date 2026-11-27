import {readFileSync} from 'node:fs';
import Ajv2020 from 'ajv/dist/2020.js';
const read=n=>JSON.parse(readFileSync(new URL(`../data/${n}.json`,import.meta.url),'utf8'));
const schema=n=>JSON.parse(readFileSync(new URL(`../schemas/${n}.schema.json`,import.meta.url),'utf8'));
export function validate(){
 const ajv=new Ajv2020({strict:false,allErrors:true});ajv.addFormat('date',/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/);ajv.addSchema(schema('common'),'common.schema.json');
 for(const name of ['runs','leaderboard','tasks','frameworks']){const check=ajv.compile(schema(name));if(!check(read(name)))throw Error(`${name} schema: ${ajv.errorsText(check.errors)}`)}
 const runs=read('runs').items,board=read('leaderboard').items,tasks=read('tasks').items,frameworks=read('frameworks').items;const fail=s=>{throw Error(s)};
 if(runs.length!==140||runs.filter(x=>x.value!==null).length!==125)fail('Unexpected coverage');
 if(new Set(runs.map(x=>x.id)).size!==140||tasks.length!==5||frameworks.length!==7||board.runs.length!==140)fail('Unexpected dimensions or duplicate cell');
 for(const r of runs){let t=tasks.find(t=>t.id===r.taskId),f=frameworks.find(f=>f.id===r.frameworkId);if(!t||!f||r.direction!==t.direction||r.metric!==t.metric)fail(`Invalid references ${r.id}`);let b=board.runs.find(x=>x.id===r.id);if(!b||b.value!==r.value||b.displayValue!==r.displayValue||b.protocol!==r.protocol)fail(`Leaderboard mismatch ${r.id}`);if(r.value===null&&(r.displayValue!==null||r.sourceValue!==null||r.paperBest))fail(`Invalid missing value ${r.id}`);if(r.taskId==='babylm'&&r.paperBest)fail('BabyLM cross-protocol best');for(const k of ['official','trajectory','judge'])if(!r.source[k])fail(`Missing ${k}`)}
 for(const a of board.availability){let actual=runs.filter(r=>r.frameworkId===a.frameworkId&&r.value!==null).length/20*100;if(actual!==a.percent)fail(`Availability mismatch ${a.frameworkId}`)}
 if(board.profiles.length!==7||board.trajectory.length!==7||board.availability.length!==7||board.reliability.length!==6)fail('Missing summary records');
 for(const p of board.profiles)if(p.conditions!==10||p.values.length!==6||p.values.some(v=>v<0||v>1))fail('Invalid profile');
 for(const p of board.trajectory)if(p.values.length!==5||p.values.some(v=>v<0||v>1))fail('Invalid trajectory');
 if(board.reliability.reduce((s,r)=>s+r.n,0)!==722||board.reliability.some(r=>r.low>r.kappa||r.high<r.kappa))fail('Invalid reliability');
 for(const t of tasks.filter(t=>t.id!=='babylm'))for(const model of [...new Set(runs.map(r=>r.model))]){const group=runs.filter(r=>r.taskId===t.id&&r.model===model&&r.value!==null);const best=t.direction==='lower'?Math.min(...group.map(r=>r.value)):Math.max(...group.map(r=>r.value));for(const r of group)if(r.paperBest!==(r.value===best))fail(`Paper-best mismatch ${r.id}`)}
 return {cells:runs.length,outcomes:runs.filter(r=>r.value!==null).length};
}
if(process.argv[1]&&import.meta.url===new URL(`file:///${process.argv[1].replaceAll('\\','/')}`).href)console.log('Validated',validate());
