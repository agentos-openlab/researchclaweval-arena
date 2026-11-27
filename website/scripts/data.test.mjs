import {test} from 'node:test'; import assert from 'node:assert/strict'; import {validate} from './validate-data.mjs';
test('frozen data preserves all design cells and missing outcomes',()=>assert.deepEqual(validate(),{cells:140,outcomes:125}));
