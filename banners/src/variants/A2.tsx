import React, {CSSProperties} from 'react';
import {useCurrentFrame} from 'remotion';
import {BUILD, LIVELY, easeIn, easeInOut, easeOut, exitP, exitStyle, mix, prog, restage, sp, wave} from '../lib/anim';
import {A_LINES, CTA, HeadlineA, HeadlineB, Subtitle} from '../lib/Headlines';
import {Mascot} from '../lib/Mascot';
import {POS, Scene} from '../lib/Scene';
import {A_SUB_TOP, B_SUB_POS, CardStack} from './common';

/* ---------------------------------------------------------------- V11
 * Seamless 8 s loop: A holds, hands over to B (+CTA), B hands back to A.
 * Loop point sits inside the A hold, so the file ends on a 1.5 s still A. */
export const V11_D = 240;
export const V11: React.FC = () => {
	const f = useCurrentFrame();
	const D = V11_D;
	const outA = 40;
	const inB = 54;
	const outB = 146;
	const inA = 160;
	const OUT = 10;
	const IN = 22;
	// A: visible at f<outA and after inA (fully settled by 195)
	const aInner = (i: number): CSSProperties => {
		if (f < inA) {
			const e = 1 - prog(f, outA + i * 3, OUT, easeIn);
			return {transform: `translateY(${(1 - e) * -110}%)`, opacity: e};
		}
		const t = prog(f, inA + i * 5, IN, easeOut);
		return {transform: `translateY(${(1 - t) * 110}%)`, opacity: prog(f, inA + i * 5, 12)};
	};
	const aPlateT = f < inA ? 1 - prog(f, outA + 4, OUT, easeIn) : prog(f, inA + 10, 20, easeOut);
	const plate: CSSProperties = {opacity: aPlateT, transform: `scale(${mix(0.8, 1, aPlateT)})`, transformOrigin: '30% 80%'};
	const bInner = (i: number): CSSProperties => {
		if (f < outB) {
			const t = prog(f, inB + i * 4, IN, easeOut);
			return {transform: `translateY(${(1 - t) * 110}%)`, opacity: prog(f, inB + i * 4, 12)};
		}
		const e = 1 - prog(f, outB + 3 + i * 3, OUT, easeIn);
		return {transform: `translateY(${(1 - e) * -110}%)`, opacity: e};
	};
	const bVisible = f >= inB && f < outB + 3 + 2 * 3 + OUT + 1;
	// shared subtitle glides between the two layouts
	// shared subtitle: fades out with the outgoing headline, relocates while hidden,
	// fades in once the incoming lines have settled (it never crosses moving text)
	const firstHalf = f < 120;
	const subIn = firstHalf ? inB + 28 : inA + 24;
	const subOut = firstHalf ? outA : outB;
	const subO = f < subIn ? 1 - prog(f, subOut, 8, easeIn) : prog(f, subIn, 10);
	const toB = firstHalf ? (f < subIn ? 0 : 1) : f < subIn ? 1 : 0;
	const subTop = mix(A_SUB_TOP, B_SUB_POS.top, toB);
	const ctaT = f < outB ? prog(f, inB + 32, 18, easeOut) : 1 - prog(f, outB, OUT, easeIn);
	const cta: CSSProperties = {opacity: ctaT, transform: `translateY(${(1 - ctaT) * 12}px) scale(${mix(0.94, 1, ctaT)})`, transformOrigin: '20% 50%'};
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} />
			<CardStack />
			<HeadlineA mask hideSub innerStyle={aInner} plateStyle={plate} glow={aPlateT} />
			{bVisible ? <HeadlineB mask innerStyle={bInner} /> : null}
			<Subtitle style={{position: 'absolute', left: 48, top: subTop, opacity: subO, letterSpacing: `${mix(0.06, 0.1, toB)}em`}} />
			{ctaT > 0 ? <CTA style={cta} /> : null}
		</Scene>
	);
};

/* ---------------------------------------------------------------- V12
 * The mascot arrives first, leans, and the headline "catches" from its side. */
export const V12_D = 240;
export const V12: React.FC = () => {
	const f = useCurrentFrame();
	const D = V12_D;
	const mIn = BUILD + 2;
	let mStyle: CSSProperties;
	let mScale = 1;
	if (f < mIn) {
		const e = exitP(f, 0);
		mStyle = {opacity: e, filter: e < 1 ? `blur(${(1 - e) * 4}px)` : undefined};
		mScale = 0.96 + 0.04 * e;
	} else {
		const s = sp(f, mIn, {damping: 16, stiffness: 100, mass: 1});
		const o = prog(f, mIn, 12);
		mStyle = {opacity: o, transform: `translateY(${(1 - s) * 40}px)`, filter: o < 1 ? `blur(${(1 - o) * 6}px)` : undefined};
		mScale = mix(0.88, 1, s);
	}
	const lean = f < mIn ? 0 : prog(f, mIn + 22, 12, easeOut) * (1 - sp(f, mIn + 40, {damping: 20, stiffness: 90}));
	const head0 = mIn + 28;
	// words arrive from the mascot's side: nearest word first
	const order = [2, 1, 0, 4, 3]; // gi -> rank (line1: jau, klientai, Jūsų; line2: per, renkasi)
	const word = (line: number, _w: number, gi: number): CSSProperties => {
		const st = head0 + order[gi] * 5 + line * 6;
		if (f < st) return exitStyle(exitP(f, 1 + line));
		const s = sp(f, st, {damping: 200, stiffness: 110});
		const o = prog(f, st, 12);
		return {opacity: o, transform: `translateX(${(1 - s) * 30}px)`, filter: o < 1 ? `blur(${(1 - o) * 6}px)` : undefined};
	};
	const plateAt = head0 + 4;
	const plate: CSSProperties =
		f < plateAt
			? exitStyle(exitP(f, 2))
			: {opacity: prog(f, plateAt, 10), transform: `translateX(${(1 - sp(f, plateAt, LIVELY)) * 60}px) scale(${mix(0.8, 1, sp(f, plateAt, LIVELY))})`, transformOrigin: '100% 80%'};
	const glow = f < plateAt ? exitP(f, 2) : prog(f, plateAt + 6, 16) * (1 + 0.4 * (1 - prog(f, plateAt + 20, 30, easeInOut)));
	const sub = restage(f, head0 + 30, 3, 10);
	const card = (i: number) => restage(f, head0 + 22 + i * 5, 1 + i, 16);
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} style={mStyle} scale={mScale} rotate={-4 * lean} lift={(f < mIn ? 3 : 3 + 3 * wave(f - mIn, D / 2)) + 4 * lean} />
			<CardStack styles={card} />
			<HeadlineA wordStyle={word} plateStyle={plate} glow={glow} subStyle={sub} />
		</Scene>
	);
};
void A_LINES;

/* ---------------------------------------------------------------- V14
 * Thin grid, corner ticks drawing in, "AI" typed with a caret. */
const Ticks: React.FC<{box: [number, number, number, number]; t: number; color: string}> = ({box, t, color}) => {
	const [x0, y0, x1, y1] = box;
	const L = 22;
	const len = L * 2;
	const corners: [number, number, number, number][] = [
		[x0, y0, 1, 1],
		[x1, y0, -1, 1],
		[x0, y1, 1, -1],
		[x1, y1, -1, -1],
	];
	return (
		<svg width={1584} height={396} style={{position: 'absolute', inset: 0}}>
			{corners.map(([x, y, sx, sy], i) => (
				<path
					key={i}
					d={`M ${x} ${y + sy * L} L ${x} ${y} L ${x + sx * L} ${y}`}
					fill="none"
					stroke={color}
					strokeWidth={1.5}
					strokeLinecap="round"
					strokeDasharray={len}
					strokeDashoffset={len * (1 - t)}
				/>
			))}
		</svg>
	);
};

export const V14_D = 240;
export const V14: React.FC = () => {
	const f = useCurrentFrame();
	const D = V14_D;
	const tickAt = BUILD + 2;
	const tickT = f < tickAt ? 1 : prog(f, tickAt, 20, easeInOut);
	const tickO = f < tickAt ? exitP(f, 0) : prog(f, tickAt, 6);
	const lineAt = (i: number) => tickAt + 8 + i * 6;
	const line = (i: number): CSSProperties => {
		const st = lineAt(i);
		if (f < st) return exitStyle(exitP(f, i * 2));
		const t = prog(f, st, 22, easeOut);
		return {clipPath: `inset(-30% ${(1 - t) * 100}% -40% 0)`, transform: `translateX(${(1 - t) * -10}px)`, opacity: prog(f, st, 8)};
	};
	const plateAt = lineAt(1) + 12;
	const plate: CSSProperties =
		f < plateAt
			? exitStyle(exitP(f, 4))
			: {opacity: prog(f, plateAt, 8), transform: `scale(${mix(0.92, 1, sp(f, plateAt, {damping: 200, stiffness: 140}))})`, transformOrigin: '0% 80%', paddingRight: 46};
	const typeAt = plateAt + 6;
	const aiTyped = f < plateAt ? undefined : f < typeAt ? 0 : f < typeAt + 4 ? 1 : 2;
	// caret: soft breathing (never a hard on/off blink)
	const caret = f < plateAt ? exitP(f, 4) : prog(f, typeAt - 2, 6) * (0.78 + 0.22 * wave(f - typeAt, 40, 0.25));
	const glow = f < plateAt ? exitP(f, 4) : prog(f, typeAt + 4, 18);
	const sub = restage(f, plateAt + 14, 4, 10);
	const card = (i: number) => restage(f, plateAt + 18 + i * 5, 1 + i, 16);
	const grid: CSSProperties = {
		position: 'absolute',
		inset: 0,
		backgroundImage:
			'linear-gradient(rgba(255,255,255,0.17) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.17) 1px, transparent 1px)',
		backgroundSize: '44px 44px',
		backgroundPosition: '0 22px',
		WebkitMaskImage: 'radial-gradient(ellipse 70% 120% at 30% 50%, #000 30%, transparent 100%)',
	};
	return (
		<Scene f={f} period={D}>
			<div style={grid} />
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} />
			<CardStack styles={card} />
			<div style={{opacity: tickO}}>
				<Ticks box={[30, 40, 744, 336]} t={tickT} color="rgba(8,30,22,0.55)" />
			</div>
			<HeadlineA lineStyle={line} plateStyle={plate} aiTyped={aiTyped} caret={caret} glow={glow} subStyle={sub} />
		</Scene>
	);
};
void CTA;
