import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {analyzeTemporalPair} from './temporalDivergence';
const paths=process.argv.slice(2);
if(!paths.length)throw new Error('Usage: node --import tsx scripts/temporal-divergence.ts PAIR_JSON [PAIR_JSON ...]; deterministic JSON to stdout only');
console.log(JSON.stringify(paths.map(path=>{const bytes=readFileSync(path);const {evolution,...summary}=analyzeTemporalPair(bytes.toString('utf8'));return {input_sha256:createHash('sha256').update(bytes).digest('hex'),...summary,sample_count:evolution.length};}),null,2));
