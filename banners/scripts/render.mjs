// Render variants: node scripts/render.mjs [v01 v02 ...]
// -> out/vNN-slug.mp4 (H.264 yuv420p crf 17), out/vNN-poster.png (frame 0, lossless),
//    work/qc/vNN/fNNN.png (frames extracted from the encoded MP4 for review)
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const want = process.argv.slice(2);
const browserExecutable = '/opt/pw-browsers/chromium';
const chromeMode = 'chrome-for-testing';
const concurrency = Number(process.env.CONC || 1); // >1 produced partially painted / AA-shifted frames (see REPORT.md)
const chromiumOptions = process.env.GL ? {gl: process.env.GL} : {};

const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public')});
const {VARIANTS} = await import(path.join(root, 'work/variants-meta.json'), {with: {type: 'json'}}).then((m) => m.default);
fs.mkdirSync(path.join(root, 'out'), {recursive: true});

for (const v of VARIANTS) {
	if (want.length && !want.includes(v.id)) continue;
	const comp = await selectComposition({serveUrl, id: v.id, browserExecutable, chromeMode, chromiumOptions});
	const mp4 = path.join(root, 'out', `${v.id}-${v.slug}.mp4`);
	const t0 = Date.now();
	await renderMedia({
		serveUrl,
		composition: comp,
		codec: 'h264',
		crf: 17,
		pixelFormat: 'yuv420p',
		imageFormat: 'png',
		x264Preset: 'slow',
		outputLocation: mp4,
		browserExecutable,
		chromeMode,
		concurrency,
		chromiumOptions,
		muted: true,
		enforceAudioTrack: false,
	});
	await renderStill({serveUrl, composition: comp, frame: 0, output: path.join(root, 'out', `${v.id}-poster.png`), browserExecutable, chromeMode, chromiumOptions});
	// QC frames from the encoded file
	const n = comp.durationInFrames;
	const pct = [0, 0.25, 0.5, 0.75, 1].map((p) => Math.min(n - 1, Math.round(p * (n - 1))));
	const frames = [...new Set([...pct, ...v.keys, ...v.contact])].sort((a, b) => a - b);
	const qdir = path.join(root, 'work/qc', v.id);
	fs.rmSync(qdir, {recursive: true, force: true});
	fs.mkdirSync(qdir, {recursive: true});
	const sel = frames.map((f) => `eq(n\\,${f})`).join('+');
	execFileSync('ffmpeg', ['-v', 'error', '-i', mp4, '-vf', `select='${sel}'`, '-vsync', '0', path.join(qdir, 'tmp-%03d.png')]);
	frames.forEach((f, i) => fs.renameSync(path.join(qdir, `tmp-${String(i + 1).padStart(3, '0')}.png`), path.join(qdir, `f${String(f).padStart(3, '0')}.png`)));
	console.log(`${v.id} ${((Date.now() - t0) / 1000).toFixed(0)}s -> ${path.basename(mp4)}`);
}
