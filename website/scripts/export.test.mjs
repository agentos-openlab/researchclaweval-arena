import {test} from 'node:test';
import assert from 'node:assert/strict';
import {serializeCsv,serializeJson} from '../lib/export.mjs';
test('CSV preserves missing values, quotes, commas, and zero',()=>{
 assert.equal(serializeCsv(['a','b','c'],[['a,"b"',null,0]]),'a,b,c\r\n"a,""b""","","0"');
});
test('JSON keeps missing results and separate provenance',()=>{
 const record={paperScore:null,sourceValue:null,official:{status:'unresolved'},trajectory:{status:'resolved'}};
 const result=JSON.parse(serializeJson([record]));
 assert.deepEqual(result.records,[record]);assert.equal(result.paperDataVersion,'2026-10-30');
});
