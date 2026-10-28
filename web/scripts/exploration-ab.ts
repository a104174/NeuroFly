import { readFileSync } from 'node:fs';
import { compareExplorationModes } from '../src/lib/explorationComparison';
import { parseNeuralLocomotion } from '../src/lib/neuralLocomotion';

const raw = readFileSync(new URL('../public/experiments/experimental_locomotion_v1.json', import.meta.url), 'utf8');
const authority = parseNeuralLocomotion(JSON.parse(raw));
const horizons = process.argv.slice(2).length ? process.argv.slice(2).map(Number) : [1500, 5000];
if (!horizons.every(Number.isSafeInteger)) throw new Error('Usage: node --import tsx scripts/exploration-ab.ts [positive tick counts...]');
console.log(JSON.stringify(horizons.map(ticks => compareExplorationModes(authority, ticks)), null, 2));
