import React, {CSSProperties} from 'react';
import {useCurrentFrame} from 'remotion';
import {BUILD, LIVELY, easeInOut, exitP, exitStyle, mix, prog, restage, sp, wave} from '../lib/anim';
import {Badge, CARD_W, CompanyCard, QueryCard} from '../lib/Cards';
import {CTA, HeadlineB, Subtitle} from '../lib/Headlines';
import {Mascot} from '../lib/Mascot';
import {POS, Scene} from '../lib/Scene';
import {B_SUB_POS, CardStack} from './common';

const ctaIn = (f: number, at: number, stagger = 0): CSSProperties => {
	if (f < at) return exitStyle(exitP(f, stagger));
	const s = sp(f, at, {damping: 20, stiffness: 120, mass: 0.9});
	const o = prog(f, at, 10);
	return {opacity: o, transform: `translateY(${(1 - s) * 12}px) scale(${mix(0.92, 1, s)})`, transformOrigin: '20% 50%', filter: o < 1 ? `blur(${(1 - o) * 4}px)` : undefined};
};

/* ---------------------------------------------------------------- V06
 * The question types out; grey competitor cards answer; then the CTA. */
export const V06_D = 270;
export const V06: React.FC = () => {
	const f = useCurrentFrame();
	const D = V06_D;
	const T0 = BUILD + 4;
	const CH = 1.25;
	const total = 46;
	const typed = f < T0 ? 0 : (f - T0) / CH;
	const tEnd = T0 + total * CH;
	const exiting = f < T0;
	const headStyle: CSSProperties = exiting ? exitStyle(exitP(f, 0)) : {};
	const caret = !exiting && f < tEnd + 30 ? 1 - prog(f, tEnd + 14, 14) : 0;
	const qAt = Math.round(tEnd) + 6;
	const card = (i: number) => restage(f, qAt + 6 + i * 5, 2 + i, 16);
	const y0 = 130;
	const subAt = qAt + 26;
	const ctaAt = subAt + 12;
	const shimmer = prog(f, ctaAt + 30, 34, easeInOut);
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 3)} />
			<QueryCard {...POS.query} style={restage(f, qAt, 1, 14)} />
			{[0, 1, 2].map((i) => (
				<CompanyCard key={i} x={POS.card.x} y={y0 + i * 68} kind="ghost" style={card(i)} />
			))}
			<HeadlineB typed={exiting ? undefined : typed} caret={caret} style={headStyle} />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS, ...restage(f, subAt, 1, 10)}} />
			<CTA style={ctaIn(f, ctaAt, 2)} shimmer={shimmer} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V07
 * The "Rekomenduojama" badge starts on a competitor's card and moves to "Jūsų įmonė". */
export const V07_D = 270;
export const V07: React.FC = () => {
	const f = useCurrentFrame();
	const D = V07_D;
	const rivalY = 126;
	const meY = 220;
	const ghostY = 314;
	const inAt = BUILD + 2;
	const card = (i: number) => restage(f, inAt + i * 5, i, 16);
	const lift = 74;
	const move = 82;
	const settled = f < inAt; // poster = final state
	const sLift = settled ? 1 : sp(f, lift, {damping: 200, stiffness: 140});
	const sMove = settled ? 1 : sp(f, move, {damping: 24, stiffness: 70, mass: 1});
	const land = settled ? 1 : prog(f, move + 26, 14);
	const by = mix(rivalY, meY, sMove) + 8.5;
	const arc = Math.sin(Math.min(1, sMove) * Math.PI) * 16; // bow outward, never across the name
	const scale = 1 + 0.07 * sLift * (1 - land);
	const badgeRight = POS.card.x + CARD_W - 17;
	const badgeStyle = card(1); // leaves and arrives with the rival card
	const rivalDim = settled ? 1 : prog(f, move + 10, 30, easeInOut);
	const meGlow = settled ? 0 : prog(f, move + 26, 10) * (1 - prog(f, move + 40, 34, easeInOut));
	const ctaAt = move + 48;
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 3)} />
			<QueryCard {...POS.query} style={card(0)} />
			<CompanyCard x={POS.card.x} y={rivalY} kind="rival" style={{...card(1), opacity: Number(card(1).opacity ?? 1) * mix(1, 0.62, rivalDim)}} />
			<CompanyCard x={POS.card.x} y={meY} kind="me" style={card(2)} glow={meGlow} />
			<CompanyCard x={POS.card.x} y={ghostY} kind="ghost" height={50} style={card(3)} />
			{/* travelling badge, drawn above the cards */}
			<div style={{position: 'absolute', top: by, right: 1584 - badgeRight, ...badgeStyle}}>
				<div style={{transform: `translateX(${arc}px) scale(${scale})`, transformOrigin: '50% 50%', filter: `drop-shadow(0 ${6 * sLift * (1 - land)}px ${10 * sLift * (1 - land)}px rgba(6,48,34,0.3))`}}>
					<Badge />
				</div>
			</div>
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS}} />
			<CTA style={ctaIn(f, ctaAt, 4)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V08
 * CTA as liquid glass: soft iridescent rim, shimmer sweeps, arrow nudge. */
export const V08_D = 210;
export const V08: React.FC = () => {
	const f = useCurrentFrame();
	const D = V08_D;
	const at = BUILD + 2;
	const sh1 = prog(f, at + 24, 32, easeInOut);
	const sh2 = prog(f, at + 112, 32, easeInOut);
	const shimmer = sh1 > 0 && sh1 < 1 ? sh1 : sh2;
	const nudge = (t0: number) => prog(f, t0, 10) * (1 - prog(f, t0 + 10, 16, easeInOut));
	const arrowX = 5 * (nudge(at + 50) + nudge(at + 138));
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} />
			<CardStack />
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS}} />
			<CTA style={ctaIn(f, at)} shimmer={shimmer} hue={40 * wave(f, D)} arrowX={arrowX} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V09
 * The mascot sways and catches a highlight; cards arrive in a cascade. */
export const V09_D = 240;
export const V09: React.FC = () => {
	const f = useCurrentFrame();
	const D = V09_D;
	const at = BUILD + 6;
	const card = (i: number): CSSProperties => {
		const st = at + i * 5;
		if (f < st) return exitStyle(exitP(f, i * 2));
		const s = sp(f, st, {damping: 200, stiffness: 100});
		const o = prog(f, st, 12);
		return {opacity: o, transform: `translateX(${(1 - s) * 28}px)`, filter: o < 1 ? `blur(${(1 - o) * 5}px)` : undefined};
	};
	const g1 = prog(f, 26, 34, easeInOut);
	const g2 = prog(f, 150, 34, easeInOut);
	const glint = g1 > 0 && g1 < 1 ? g1 : g2;
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} rotate={2.2 * wave(f, D / 2)} lift={4 + 4 * wave(f, D / 2, 0.25)} glint={glint} glintStrength={0.32} />
			<CardStack styles={card} />
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS}} />
			<CTA />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V10
 * Minimal motion for a conservative audience: breathing mascot, slow light, one quiet CTA sheen. */
export const V10_D = 180;
export const V10: React.FC = () => {
	const f = useCurrentFrame();
	const D = V10_D;
	return (
		<Scene f={f} period={D} amp={0.7}>
			<Mascot {...POS.mascot} lift={2 + 2 * wave(f, D)} scale={1 + 0.004 * wave(f, D)} />
			<CardStack />
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS}} />
			<CTA shimmer={prog(f, 60, 44, easeInOut)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V13
 * Dark version with a neon mint accent on "o ne jus?". */
export const V13_D = 240;
export const V13: React.FC = () => {
	const f = useCurrentFrame();
	const D = V13_D;
	const inner = (i: number): CSSProperties => {
		const st = BUILD + 2 + i * 5;
		if (f < st) {
			const e = exitP(f, i * 2);
			return {transform: `translateY(${(1 - e) * -60}%)`, opacity: e};
		}
		const s = sp(f, st, {damping: 200, stiffness: 100});
		const o = prog(f, st, 14);
		return {transform: `translateY(${(1 - s) * 110}%)`, opacity: o};
	};
	const neonAt = BUILD + 26;
	const neon = f < neonAt ? exitP(f, 4) : prog(f, neonAt, 30, easeInOut);
	const card = (i: number) => restage(f, BUILD + 14 + i * 5, i, 16);
	const ctaAt = BUILD + 44;
	return (
		<Scene f={f} period={D} dark>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} shadow={0.8} />
			<CardStack theme="dark" styles={card} />
			<HeadlineB
				mask
				innerStyle={inner}
				color="#F2FFF9"
				accent="#52FFBA"
				accentStyle={{textShadow: `0 0 ${16 * neon}px rgba(82,255,186,${0.55 * neon}), 0 0 ${40 * neon}px rgba(82,255,186,${0.3 * neon})`}}
			/>
			<Subtitle italic color="rgba(220,255,240,0.82)" style={{position: 'absolute', ...B_SUB_POS, ...restage(f, BUILD + 20, 2, 10)}} />
			<CTA theme="dark" style={ctaIn(f, ctaAt, 3)} hue={40 * wave(f, D)} glow={0.5 + 0.5 * wave(f, D / 2)} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V15
 * Three cards cascade, the badge lands, CTA, then a 3 s still hold. */
export const V15_D = 270;
export const V15: React.FC = () => {
	const f = useCurrentFrame();
	const at = BUILD + 2;
	const card = (i: number) => restage(f, at + [0, 10, 16, 22][i], i, 22, i === 1 ? LIVELY : undefined);
	const bAt = at + 34;
	const badge: CSSProperties =
		f < bAt
			? f < at
				? exitStyle(exitP(f, 1))
				: {opacity: 0}
			: {opacity: prog(f, bAt, 8), transform: `translateX(${(1 - sp(f, bAt, LIVELY)) * 10}px) scale(${mix(0.6, 1, sp(f, bAt, LIVELY))})`};
	const ctaAt = at + 52;
	return (
		<Scene f={f} period={V15_D} still>
			<Mascot {...POS.mascot} lift={3} />
			<CardStack styles={card} badge={badge} />
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', ...B_SUB_POS}} />
			<CTA style={ctaIn(f, ctaAt, 4)} />
		</Scene>
	);
};
