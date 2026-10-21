import React, {CSSProperties} from 'react';
import {useCurrentFrame} from 'remotion';
import {BUILD, LIVELY, clamp, easeIn, easeInOut, easeOut, exitP, exitStyle, mix, prog, restage, sp, wave} from '../lib/anim';
import {CompanyCard, QueryCard} from '../lib/Cards';
import {A_LINES, B_LINES, CTA, HeadlineA, HeadlineB, Subtitle} from '../lib/Headlines';
import {RigMascot, blinks, hop, hops} from '../lib/Rig';
import {POS, Scene} from '../lib/Scene';
import {A_SUB_TOP, B_SUB_POS, CardStack} from './common';

/* Character variants: the mascot is rigged (scripts/rig.py) and acts; every variant pairs it with its own text mechanic. */

const M = POS.mascot;
/** subtle breathing, periodic over `period` */
const breathe = (f: number, period: number) => {
	const w = wave(f, period / Math.max(1, Math.round(period / 90)));
	return {sy: 1 + 0.012 * w, sx: 1 - 0.008 * w};
};
/** eased value that moves between keyframes [frame, value][] */
const track = (f: number, keys: [number, number][], dur = 12) => {
	let v = keys[0][1];
	for (let i = 1; i < keys.length; i++) v = mix(v, keys[i][1], prog(f, keys[i][0], dur, easeInOut));
	return v;
};
const pop = (f: number, at: number, dist = 20): CSSProperties => {
	const s = sp(f, at, LIVELY);
	const o = prog(f, at, 8);
	return {opacity: o, transform: `translateY(${(1 - s) * dist}px) scale(${mix(0.6, 1, s)})`, transformOrigin: '50% 80%'};
};
const ctaIn = (f: number, at: number, stagger = 0): CSSProperties => {
	if (f < at) return exitStyle(exitP(f, stagger));
	const s = sp(f, at, {damping: 20, stiffness: 120, mass: 0.9});
	const o = prog(f, at, 10);
	return {opacity: o, transform: `translateY(${(1 - s) * 12}px) scale(${mix(0.92, 1, s)})`, transformOrigin: '20% 50%'};
};
const plateIn = (f: number, at: number, stagger = 4): CSSProperties =>
	f < at
		? exitStyle(exitP(f, stagger))
		: {opacity: prog(f, at, 8), transform: `scale(${mix(0.6, 1, sp(f, at, LIVELY))})`, transformOrigin: '30% 80%'};
const glowIn = (f: number, at: number) => (f < at ? exitP(f, 4) : prog(f, at + 4, 14) * (1 + 0.45 * (1 - prog(f, at + 18, 30, easeInOut))));
const mascotExit = (f: number): CSSProperties => {
	const e = exitP(f, 0);
	return {opacity: e, transform: `translateY(${(1 - e) * 10}px)`, filter: e < 1 ? `blur(${(1 - e) * 4}px)` : undefined};
};

/* ---------------------------------------------------------------- V16
 * The mascot hops in from the right; each landing "drops" the next piece of the headline. */
export const V16_D = 270;
export const V16: React.FC = () => {
	const f = useCurrentFrame();
	const D = V16_D;
	const poster = f < BUILD;
	const H: [number, number, number][] = [
		[26, 16, 46],
		[47, 14, 34],
		[66, 12, 20],
	];
	const xs = [640, 420, 190, 0]; // starts half in frame, so the first frames are never empty
	let dx = xs[0];
	H.forEach(([s, a], i) => {
		if (f >= s) dx = mix(xs[i], xs[i + 1], easeInOut(clamp((f - s) / a)));
	});
	const j = hops(f, H);
	const land = H.map(([s, a]) => s + a);
	const b = breathe(f, D);
	const look = poster ? -0.4 : track(f, [[0, -1], [land[2] + 14, -0.8], [104, 0.8], [132, -0.4]], 14);
	const lookY = poster ? 0 : track(f, [[0, 0], [land[2] + 14, 0.2], [104, 0.3], [132, 0]], 14);
	const word = (_l: number, _w: number, gi: number) => {
		const at = gi < 3 ? land[0] + gi * 3 : land[1] + (gi - 3) * 3;
		return f < at ? exitStyle(exitP(f, 1)) : pop(f, at);
	};
	const card = (i: number) => restage(f, 102 + i * 5, 1 + i, 16);
	return (
		<Scene f={f} period={D}>
			<RigMascot
				{...M}
				dx={poster ? 0 : dx}
				lift={j.lift}
				sx={j.sx * b.sx}
				sy={j.sy * b.sy}
				tilt={poster ? 0 : f < land[2] ? -3 * Math.sin(Math.PI * clamp((f - 26) / (land[2] - 26))) : 0}
				lookX={look}
				lookY={lookY}
				blink={blinks(f, [90, 160, 224])}
				style={f < BUILD ? mascotExit(f) : undefined}
			/>
			<CardStack styles={card} />
			<HeadlineA wordStyle={word} plateStyle={plateIn(f, land[2])} glow={glowIn(f, land[2])} subStyle={restage(f, 96, 4, 10)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V17
 * The mascot reads along: its eyes follow each line, then the cards, then the CTA.
 * Text: line mask reveal + a glass highlighter sweeping behind "konkurentus,". */
export const V17_D = 270;
export const V17: React.FC = () => {
	const f = useCurrentFrame();
	const D = V17_D;
	const L0 = BUILD + 2;
	const inner = (i: number): CSSProperties => {
		const st = L0 + i * 12;
		if (f < st) {
			const e = exitP(f, i * 2);
			return {transform: `translateY(${(1 - e) * -60}%)`, opacity: e};
		}
		const s = sp(f, st, {damping: 200, stiffness: 100});
		return {transform: `translateY(${(1 - s) * 110}%)`, opacity: prog(f, st, 12)};
	};
	const hl = f < L0 ? 1 : prog(f, L0 + 34, 18, easeInOut);
	const word = (line: number, w: number): CSSProperties | undefined =>
		line === 1 && w === 1
			? {
					backgroundImage: 'linear-gradient(rgba(255,255,255,0.55), rgba(255,255,255,0.55))',
					backgroundRepeat: 'no-repeat',
					backgroundSize: `${hl * 100}% 46%`,
					backgroundPosition: '0 78%',
					borderRadius: 6,
					padding: '0 4px',
					margin: '0 -4px',
				}
			: undefined;
	const cardsAt = L0 + 60;
	const ctaAt = cardsAt + 40;
	const card = (i: number) => restage(f, cardsAt + i * 6, 1 + i, 16);
	const poster = f < L0;
	const lookX = poster ? -0.9 : track(f, [[0, -1], [L0, -1], [cardsAt, 0.9], [cardsAt + 22, 1], [ctaAt, -0.9]], 14);
	const lookY = poster ? 0.9 : track(f, [[0, -0.6], [L0 + 12, -0.1], [L0 + 24, 0.4], [cardsAt, -0.5], [cardsAt + 12, 0.2], [cardsAt + 22, 0.6], [ctaAt, 0.9]], 12);
	const nod = prog(f, ctaAt + 8, 8, easeInOut) * (1 - prog(f, ctaAt + 16, 12, easeInOut));
	const tilt = poster ? -1.5 : track(f, [[0, 0], [cardsAt, 2.5], [ctaAt, -1.5]], 18) - 3 * nod;
	const b = breathe(f, D);
	return (
		<Scene f={f} period={D}>
			<RigMascot {...M} sx={b.sx} sy={b.sy} tilt={tilt} lookX={lookX} lookY={lookY} blink={blinks(f, [56, 150, 222])} />
			<CardStack styles={card} />
			<HeadlineB mask innerStyle={inner} wordStyle={word} />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS, ...restage(f, cardsAt + 20, 2, 10)}} />
			<CTA style={ctaIn(f, ctaAt, 3)} shimmer={prog(f, ctaAt + 24, 30, easeInOut)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V18
 * The mascot peeks up from below the frame, looks around, pops up;
 * the headline cascades in letter by letter while it watches. */
export const V18_D = 240;
export const V18: React.FC = () => {
	const f = useCurrentFrame();
	const D = V18_D;
	const poster = f < BUILD;
	const peek = sp(f, BUILD + 2, {damping: 200, stiffness: 70});
	const up = sp(f, 82, {damping: 11, stiffness: 120, mass: 0.8});
	const lift = poster ? 0 : mix(-330, -170, peek) + 170 * up;
	const stretch = poster ? 0 : 0.08 * Math.sin(Math.PI * clamp((f - 82) / 12)) * (f >= 82 ? 1 : 0);
	const landSq = poster ? 0 : 0.08 * (f > 94 ? 1 - sp(f, 94, {damping: 9, stiffness: 200, mass: 0.6}) : 0);
	const lookX = poster ? -0.6 : track(f, [[0, 0], [44, -1], [58, 1], [72, -0.2], [100, -1], [150, -0.6]], 10);
	const lookY = poster ? -0.2 : track(f, [[0, -0.8], [100, -0.4], [150, -0.2]], 12);
	const C0 = 100;
	const ch = (_l: number, ci: number): CSSProperties => {
		const at = C0 + ci * 1.2;
		if (f < at) return exitStyle(exitP(f, 0));
		const s = sp(f, at, {damping: 14, stiffness: 140, mass: 0.7});
		const o = prog(f, at, 6);
		return {opacity: o, transform: `translateY(${(1 - s) * 34}px) rotate(${(1 - s) * 6}deg)`, transformOrigin: '50% 100%'};
	};
	const aiAt = C0 + 25 * 1.2 + 4;
	const card = (i: number) => restage(f, aiAt + 20 + i * 5, 1 + i, 16);
	const b = breathe(f, D);
	return (
		<Scene f={f} period={D}>
			<RigMascot
				{...M}
				lift={lift}
				sx={b.sx * (1 - stretch * 0.6 + landSq * 0.7)}
				sy={b.sy * (1 + stretch - landSq)}
				lookX={lookX}
				lookY={lookY}
				blink={blinks(f, [76, 180])}
				style={f < BUILD ? mascotExit(f) : undefined}
			/>
			<CardStack styles={card} />
			<HeadlineA charStyle={ch} plateStyle={plateIn(f, aiAt)} glow={glowIn(f, aiAt)} subStyle={restage(f, aiAt + 12, 4, 10)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V19
 * Mood story: the mascot is happy, sees the competitors recommended and deflates,
 * then "Jūsų įmonė" earns the badge and it hops with joy. */
export const V19_D = 300;
export const V19: React.FC = () => {
	const f = useCurrentFrame();
	const D = V19_D;
	const poster = f < BUILD;
	const W0 = BUILD + 2;
	const word = (line: number, _w: number, gi: number): CSSProperties => {
		const at = W0 + gi * 4 + line * 8 + (line === 2 ? 20 : 0);
		if (f < at) return exitStyle(exitP(f, line));
		const s = sp(f, at, {damping: 200, stiffness: 120});
		const o = prog(f, at, 10);
		const em = line === 2 ? 1 + 0.08 * (prog(f, at + 6, 8) * (1 - prog(f, at + 14, 16, easeInOut))) : 1;
		return {opacity: o, transform: `translateY(${(1 - s) * 18}px) scale(${em})`, transformOrigin: '0% 80%', filter: o < 1 ? `blur(${(1 - o) * 5}px)` : undefined};
	};
	const ghostsAt = W0 + 30;
	const sadAt = ghostsAt + 16;
	const meAt = 132;
	const joy = 140;
	const ghostY = (i: number) => mix(POS.card.y + i * 68, [POS.ghost1.y, POS.ghost2.y, 360][i], poster ? 1 : sp(f, meAt - 4, {damping: 200, stiffness: 90}));
	const ghost = (i: number): CSSProperties => {
		const base = restage(f, ghostsAt + i * 5, 1 + i, 16);
		const gone = i === 2 ? (poster ? 1 : prog(f, meAt - 4, 10)) : 0; // third ghost leaves to make room
		return {...base, opacity: Number(base.opacity ?? 1) * (1 - gone)};
	};
	const me: CSSProperties = f < BUILD ? exitStyle(exitP(f, 2)) : {...pop(f, meAt, 24), transformOrigin: '50% 50%'};
	const badge: CSSProperties | null = f < BUILD ? exitStyle(exitP(f, 2)) : f < meAt + 10 ? null : pop(f, meAt + 10, 6);
	const j = hop(f, joy, 14, 18); // low enough that the head never leaves the frame
	const sad = poster ? 0 : prog(f, sadAt, 16, easeInOut) * (1 - prog(f, joy - 6, 10, easeInOut));
	const lookX = poster ? -0.9 : track(f, [[0, -0.9], [ghostsAt, 1], [W0 + 52, -0.2], [meAt, 1], [170, -0.9]], 12);
	const lookY = poster ? 0.9 : track(f, [[0, -0.5], [ghostsAt, 0.4], [W0 + 52, 0], [meAt, -0.3], [170, 0.9]], 12);
	const b = breathe(f, D);
	const ctaAt = 168;
	return (
		<Scene f={f} period={D}>
			<RigMascot
				x={M.x}
				y={M.y + 10} // headroom for the joy hop
				lift={j.lift}
				sx={(1 + (j.sx - 1) * 0.5) * b.sx * (1 + 0.02 * sad)}
				sy={(1 + (j.sy - 1) * 0.5) * b.sy * (1 - 0.035 * sad)}
				tilt={2.5 * sad}
				lookX={lookX}
				lookY={lookY + 0.3 * sad}
				smile={mix(1, 0.2, sad) + 0.2 * prog(f, joy, 10) * (poster ? 0 : 1)}
				eyes={1 + 0.08 * (poster ? 0 : prog(f, W0 + 52, 8) * (1 - prog(f, W0 + 70, 12)))}
				blink={blinks(f, [60, 200, 262])}
			/>
			<QueryCard {...POS.query} style={restage(f, ghostsAt - 6, 0, 14)} />
			{[0, 1, 2].map((i) => (
				<CompanyCard key={i} x={POS.card.x} y={ghostY(i)} kind="ghost" style={ghost(i)} />
			))}
			<CompanyCard {...POS.card} kind="me" badge={badge} style={me} glow={poster ? 0 : prog(f, meAt + 10, 8) * (1 - prog(f, meAt + 24, 30, easeInOut))} />
			<HeadlineB wordStyle={word} />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS, ...restage(f, ctaAt - 10, 3, 10)}} />
			<CTA style={ctaIn(f, ctaAt, 4)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V20
 * Focus-pull words; "AI" drops in, the mascot is surprised and nods twice. */
export const V20_D = 240;
export const V20: React.FC = () => {
	const f = useCurrentFrame();
	const D = V20_D;
	const poster = f < BUILD;
	const W0 = BUILD + 2;
	const word = (_l: number, _w: number, gi: number): CSSProperties => {
		const at = W0 + gi * 5;
		if (f < at) return exitStyle(exitP(f, 1));
		const t = prog(f, at, 18, easeOut);
		return {opacity: prog(f, at, 10), transform: `scale(${mix(1.3, 1, t)})`, filter: t < 1 ? `blur(${(1 - t) * 12}px)` : undefined, transformOrigin: '50% 60%'};
	};
	const aiAt = W0 + 32;
	const plate: CSSProperties =
		f < aiAt
			? exitStyle(exitP(f, 4))
			: {opacity: prog(f, aiAt, 6), transform: `translateY(${(1 - sp(f, aiAt, {damping: 12, stiffness: 160, mass: 0.8})) * -70}px)`};
	const surprise = poster ? 0 : prog(f, aiAt + 6, 5) * (1 - prog(f, aiAt + 20, 14, easeInOut));
	const j = hop(f, aiAt + 6, 10, 12);
	const nod = (at: number) => prog(f, at, 7, easeInOut) * (1 - prog(f, at + 7, 9, easeInOut));
	const nods = poster ? 0 : nod(aiAt + 36) + nod(aiAt + 54);
	const lookX = poster ? -0.7 : track(f, [[0, -1], [aiAt, -0.7], [aiAt + 76, 0.8], [aiAt + 100, -0.7]], 12);
	const lookY = poster ? 0.3 : track(f, [[0, -0.5], [aiAt, 0.3], [aiAt + 76, 0], [aiAt + 100, 0.3]], 12);
	const card = (i: number) => restage(f, aiAt + 70 + i * 5, 1 + i, 16);
	const b = breathe(f, D);
	return (
		<Scene f={f} period={D}>
			<RigMascot
				{...M}
				lift={j.lift}
				sx={j.sx * b.sx}
				sy={j.sy * b.sy}
				tilt={-4 * nods}
				lookX={lookX}
				lookY={lookY + 0.6 * nods}
				eyes={1 + 0.12 * surprise}
				smile={1 + 0.25 * surprise}
				blink={blinks(f, [W0 + 18, 170, 220])}
			/>
			<CardStack styles={card} />
			<HeadlineA wordStyle={word} plateStyle={plate} glow={glowIn(f, aiAt)} subStyle={restage(f, aiAt + 60, 4, 10)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V21
 * Dark: the mascot "wakes up" (double blink, glow, smile); text draws as a neon
 * outline, then fills. */
export const V21_D = 240;
export const V21: React.FC = () => {
	const f = useCurrentFrame();
	const D = V21_D;
	const poster = f < BUILD;
	const L0 = BUILD + 2;
	const line = (i: number): CSSProperties => {
		const st = L0 + i * 7;
		if (f < st) return exitStyle(exitP(f, i * 2));
		const t = prog(f, st, 26, easeInOut);
		return {clipPath: `inset(-30% ${(1 - t) * 100}% -40% 0)`};
	};
	const fill = poster ? 1 : prog(f, L0 + 40, 24, easeInOut);
	const wake = poster ? 1 : prog(f, 58, 30, easeInOut);
	const card = (i: number) => restage(f, 92 + i * 5, 1 + i, 16);
	const lookX = poster ? -0.8 : track(f, [[0, 0], [52, -0.9], [96, 0.9], [120, -0.8]], 12);
	const lookY = poster ? 0.2 : track(f, [[0, 0.4], [52, -0.4], [96, 0.2], [120, 0.2]], 12);
	return (
		<Scene f={f} period={D} dark>
			<RigMascot
				{...M}
				opacity={mix(0.55, 1, wake)}
				glow={0.6 * wake + 0.12 * wake * wave(f, D / 2)}
				lookX={lookX}
				lookY={lookY}
				smile={mix(0.6, 1, wake)}
				blink={poster ? 0 : Math.max(f < 40 ? 0.85 : 0, blinks(f, [44, 52, 170]))}
				sy={1 + 0.012 * wave(f, D / 2)}
			/>
			<CardStack theme="dark" styles={card} />
			<HeadlineB
				lineStyle={line}
				color={`rgba(242,255,249,${fill})`}
				accent={`rgba(82,255,186,${fill})`}
				style={{WebkitTextStroke: `1.4px rgba(82,255,186,${0.9 * (1 - fill) + 0.0})`}}
				accentStyle={{textShadow: `0 0 ${16 * fill}px rgba(82,255,186,${0.55 * fill})`}}
			/>
			<Subtitle italic color="rgba(220,255,240,0.82)" style={{position: 'absolute', ...B_SUB_POS, ...restage(f, L0 + 56, 2, 10)}} />
			<CTA theme="dark" style={ctaIn(f, 110, 3)} hue={40 * wave(f, D)} glow={0.5 + 0.5 * wave(f, D / 2)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V22
 * Seamless 9 s loop A -> B -> A. Letters drop out and rise in; the mascot hops at each
 * hand-over and looks at whatever just changed. Loop point sits in the A hold. */
export const V22_D = 276;
export const V22: React.FC = () => {
	const f = useCurrentFrame();
	const D = V22_D;
	// each entrance starts only after the outgoing letters are gone (exit sweep = n*0.5 + 9 frames)
	const outA = 46;
	const inB = 72;
	const outB = 160;
	const inA = 192;
	const CH = 0.8;
	const aChar = (_l: number, ci: number): CSSProperties => {
		if (f < 120) {
			const t = prog(f, outA + ci * 0.5, 9, easeIn);
			return {opacity: 1 - t, transform: `translateY(${t * 26}px)`};
		}
		const t = sp(f, inA + ci * CH, {damping: 200, stiffness: 140});
		return {opacity: prog(f, inA + ci * CH, 6), transform: `translateY(${(1 - t) * -26}px)`};
	};
	const bChar = (_l: number, ci: number): CSSProperties => {
		if (f < 140) {
			const t = sp(f, inB + ci * CH, {damping: 200, stiffness: 140});
			return {opacity: prog(f, inB + ci * CH, 6), transform: `translateY(${(1 - t) * -26}px)`};
		}
		const t = prog(f, outB + ci * 0.5, 9, easeIn);
		return {opacity: 1 - t, transform: `translateY(${t * 26}px)`};
	};
	const aPlate = f < 120 ? 1 - prog(f, outA + 8, 9, easeIn) : prog(f, inA + 18, 14, easeOut);
	const bOn = f >= inB && f < inA;
	const ctaT = f < 140 ? prog(f, inB + 44, 16, easeOut) : 1 - prog(f, outB, 9, easeIn);
	const firstHalf = f < 140;
	const subIn = firstHalf ? inB + 40 : inA + 26;
	const subOut = firstHalf ? outA : outB;
	const subO = f < subIn ? 1 - prog(f, subOut, 8, easeIn) : prog(f, subIn, 10);
	const toB = firstHalf ? (f < subIn ? 0 : 1) : f < subIn ? 1 : 0;
	const j = hops(f, [
		[outA + 8, 12, 18],
		[outB + 8, 12, 18],
	]);
	const lookX = track(f, [[0, -0.6], [34, 0.9], [outA - 2, -0.6], [inB + 50, -0.8], [outB - 10, 0.9], [outB, -0.6]], 10);
	const lookY = track(f, [[0, 0], [34, 0.3], [outA - 2, 0], [inB + 50, 0.9], [outB - 10, 0.3], [outB, 0]], 10);
	const b = breathe(f, D);
	return (
		<Scene f={f} period={D}>
			<RigMascot {...M} lift={j.lift} sx={j.sx * b.sx} sy={j.sy * b.sy} lookX={lookX} lookY={lookY} blink={blinks(f, [26, 130, 244])} />
			<CardStack />
			<HeadlineA hideSub charStyle={aChar} plateStyle={{opacity: aPlate, transform: `scale(${mix(0.8, 1, aPlate)})`, transformOrigin: '30% 80%'}} glow={aPlate} />
			{bOn ? <HeadlineB charStyle={bChar} /> : null}
			<Subtitle style={{position: 'absolute', left: 48, top: mix(A_SUB_TOP, B_SUB_POS.top, toB), opacity: subO, letterSpacing: `${mix(0.06, 0.1, toB)}em`}} />
			{ctaT > 0 ? <CTA style={{opacity: ctaT, transform: `translateY(${(1 - ctaT) * 12}px) scale(${mix(0.94, 1, ctaT)})`, transformOrigin: '20% 50%'}} /> : null}
		</Scene>
	);
};
void A_LINES;
void B_LINES;
