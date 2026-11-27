import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const data=n=>JSON.parse(readFileSync(new URL(`../data/${n}.json`,import.meta.url),'utf8')).items;
const root=new URL('../../',import.meta.url);
const paper=JSON.parse(readFileSync(new URL('generated/english/tables.json',root),'utf8'));
const radar=JSON.parse(readFileSync(new URL('generated/english/radar-data.json',root),'utf8'));
const index=JSON.parse(readFileSync(new URL('results/snapshots/server-paper-20261025T105508Z/paper/experiments_20261019/source_provenance.json',root),'utf8')).rows;
const table=id=>paper.find(t=>t.table===id).rows;const runs=data('runs'),board=data('leaderboard'),frameworks=data('frameworks');
const ids=['arc','mc','babylm','psydef','tdc'],models=['GPT-6-Luna','GPT-5.6-Luna','DeepSeek-V4','Kimi-K2.6'];let matrix=table('7').slice(1),checked=0;
for(let t=0;t<5;t++)for(let f=0;f<7;f++)for(let m=0;m<4;m++){const row=matrix[t*7+f],cell=row[m+1],run=runs.find(x=>x.taskId===ids[t]&&x.frameworkId===frameworks[f].id&&x.model===models[m]);assert.equal(row[0],frameworks[f].name);assert.equal(run.displayValue,cell==='N/A'?null:cell.replaceAll('*',''));assert.equal(run.paperBest,ids[t]!=='babylm'&&cell.includes('**'));const source=index.find(x=>x.framework===run.frameworkId&&x.topic===run.taskId&&x.model===run.model);assert.equal(run.sourceValue,run.value===null?null:source.official.snapshot_values.official_final??null);if(run.sourceValue!==null){const parts=run.displayValue.toLowerCase().split('e'), decimals=(parts[0].split('.')[1]||'').length, tolerance=0.5*10**(Number(parts[1]||0)-decimals);assert.ok(Math.abs(run.value-run.sourceValue)<=tolerance+Math.max(1e-12,Math.abs(run.value)*1e-12),`Outside paper rounding: ${run.id}`)}for(const role of ['official','trajectory','judge']){assert.equal(run.source[role].status,source[role]?.status??'unknown');assert.equal(run.source[role].recordId,source[role]?.snapshot_basename||null)}checked++}
for(const [i,row] of table('6').slice(1,-1).entries()){assert.equal(board.availability[i].percent,Number(row[1].replace('%','')))}
for(const [i,row] of table('9').slice(1).entries()){assert.deepEqual(board.profiles[i].values,row.slice(1).map(Number));for(const [j,code] of ['pq','pea','er','ou','ecc','sc'].entries()){const point=radar.points.find(p=>p.framework===board.profiles[i].frameworkId&&p.dimension===code);assert.equal(point.common_n,10);assert.ok(Math.abs(point.matched-board.profiles[i].values[j])<0.0000001)}}
for(const [i,row] of table('8a').slice(1).entries())assert.deepEqual(board.trajectory[i].values,row.slice(1).map(Number));
const expected=[[133,.594,.415,.279,.540],[131,.634,.694,.586,.778],[77,.623,.355,.172,.512],[130,.515,.490,.363,.601],[131,.527,.526,.398,.630],[120,.625,.533,.381,.664]];
assert.deepEqual(board.reliability.map(r=>[r.n,r.exact,r.kappa,r.low,r.high]),expected);
for(const [i,row] of table('judge_agreement').slice(1).entries()){const r=board.reliability[i];assert.equal(r.dimension,row[0]);assert.equal(r.n,Number(row[1]));assert.equal(r.exact,Number(row[2]));assert.equal(`${r.kappa.toFixed(3)} [${r.low.toFixed(3)}, ${r.high.toFixed(3)}]`,row[3])}
assert.deepEqual(board.referencePpl,table('7e').slice(1).map(r=>({framework:r[0],model:r[1],value:r[2]})));
console.log(`Paper audit passed: ${checked} matrix cells and source roles; 7 availability rows; 42 radar coordinates; 35 trajectory values; 6 reliability rows; 3 shared-reference values.`);
