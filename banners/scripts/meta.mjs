// dump variant metadata (ids, slugs, frames, key frames) from src/variants/index.ts for the node scripts
import fs from 'node:fs';
const src = fs.readFileSync(new URL('../src/variants/index.ts', import.meta.url), 'utf8');
const durs = {};
for (const f of ['A1', 'A2', 'B1']) {
	const s = fs.readFileSync(new URL(`../src/variants/${f}.tsx`, import.meta.url), 'utf8');
	for (const m of s.matchAll(/export const (V\d+)_D = (\d+);/g)) durs[m[1]] = +m[2];
}
const VARIANTS = [...src.matchAll(/\{id: '(v\d+)', slug: '([^']+)', component: (V\d+), frames: V\d+_D, keys: \[([^\]]*)\], contact: \[([^\]]*)\]\}/g)].map((m) => ({
	id: m[1], slug: m[2], frames: durs[m[3]], keys: m[4].split(',').map(Number), contact: m[5].split(',').map(Number),
}));
fs.mkdirSync(new URL('../work/', import.meta.url), {recursive: true});
fs.writeFileSync(new URL('../work/variants-meta.json', import.meta.url), JSON.stringify({VARIANTS}, null, 1));
console.log(VARIANTS.length, 'variants');
