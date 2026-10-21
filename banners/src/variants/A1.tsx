import React, {CSSProperties} from 'react';
import {useCurrentFrame} from 'remotion';
import {BUILD, LIVELY, easeInOut, exitP, exitStyle, mix, prog, restage, riseStyle, sp, wave} from '../lib/anim';
import {CompanyCard, GHOST_H, CARD_H, QueryCard} from '../lib/Cards';
import {HeadlineA} from '../lib/Headlines';
import {Mascot} from '../lib/Mascot';
import {POS, Scene} from '../lib/Scene';
import {CardStack} from './common';

/* ---------------------------------------------------------------- V01
 * Line-by-line mask reveal; "AI" grows with a glow bloom. */
export const V01_D = 210;
export const V01: React.FC = () => {
	const f = useCurrentFrame();
	const D = V01_D;
	const lineStart = (i: number) => BUILD + 2 + i * 6;
	const inner = (i: number): CSSProperties => {
		const st = lineStart(i);
		if (f < st) {
			const e = exitP(f, i * 2);
			return {transform: `translateY(${(1 - e) * -60}%)`, opacity: e};
		}
		const s = sp(f, st, {damping: 200, stiffness: 100});
		const o = prog(f, st, 14);
		return {transform: `translateY(${(1 - s) * 110}%)`, opacity: o, filter: o < 1 ? `blur(${(1 - o) * 5}px)` : undefined};
	};
	const aiStart = BUILD + 16;
	let plate: CSSProperties;
	let glow = 1 + 0.06 * wave(f, D / 2, 0.25);
	if (f < aiStart) {
		const e = exitP(f, 4);
		plate = {opacity: e, transform: `scale(${0.96 + 0.04 * e})`};
		glow *= e;
	} else {
		const s = sp(f, aiStart, LIVELY);
		const o = prog(f, aiStart, 10);
		plate = {opacity: o, transform: `scale(${mix(0.55, 1, s)})`, transformOrigin: '30% 80%'};
		const bloom = prog(f, aiStart + 6, 14) * (1 + 0.7 * (1 - prog(f, aiStart + 20, 34, easeInOut)));
		glow = bloom * (1 + 0.06 * wave(f, D / 2, 0.25));
	}
	const subStart = BUILD + 30;
	const sub: CSSProperties =
		f < subStart
			? exitStyle(exitP(f, 4))
			: {...riseStyle(f, subStart, 10), letterSpacing: `${mix(0.24, 0.06, prog(f, subStart, 26))}em`};
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} />
			<CardStack />
			<HeadlineA mask innerStyle={inner} plateStyle={plate} glow={glow} subStyle={sub} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V02
 * The ChatGPT query types first; the answer cards land; then the headline. */
export const V02_D = 270;
export const V02: React.FC = () => {
	const f = useCurrentFrame();
	const D = V02_D;
	const qIn = BUILD + 2;
	const typeStart = qIn + 12;
	const CH = 1.2;
	const typed = f < typeStart ? 0 : (f - typeStart) / CH;
	const typeEnd = typeStart + 37 * CH;
	const cardsIn = Math.round(typeEnd) + 18;
	const headIn = cardsIn + 20;
	// the query types large on the left, then docks into its slot as the answers arrive
	const dockAt = cardsIn - 8;
	// rise first, then slide right, so the card passes above the mascot's head
	const sUp = f < qIn ? 1 : sp(f, dockAt, {damping: 200, stiffness: 140});
	const sDock = f < qIn ? 1 : sp(f, dockAt + 5, {damping: 200, stiffness: 100});
	const qx = mix(46, POS.query.x, sDock);
	const qy = mix(150, POS.query.y, sUp);
	const qScale = mix(1.3, 1, sUp);
	const qStyle: CSSProperties =
		f < qIn
			? exitStyle(exitP(f, 0))
			: (() => {
					const s = sp(f, qIn, {damping: 200, stiffness: 110});
					const o = prog(f, qIn, 10);
					return {opacity: o, transform: `translateY(${(1 - s) * 14}px) scale(${qScale * mix(0.94, 1, s)})`, transformOrigin: '0 0'};
				})();
	// caret: solid while typing, fades once the answer arrives
	const caret = f >= typeStart && f < cardsIn + 14 ? 1 - prog(f, cardsIn, 14) : 0;
	const card = (i: number) => restage(f, cardsIn + (i - 1) * 5, i, 16);
	const word = (_l: number, _w: number, gi: number) => restage(f, headIn + gi * 4, 2, 22, {damping: 200, stiffness: 120});
	const plateIn = headIn + 22;
	const plate: CSSProperties =
		f < plateIn
			? exitStyle(exitP(f, 4))
			: {opacity: prog(f, plateIn, 10), transform: `scale(${mix(0.7, 1, sp(f, plateIn, LIVELY))})`, transformOrigin: '30% 80%'};
	const glow = f < plateIn ? exitP(f, 4) : prog(f, plateIn + 4, 18) * (1 + 0.4 * (1 - prog(f, plateIn + 18, 30, easeInOut)));
	const sub = restage(f, plateIn + 12, 4, 10);
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 3)} />
			<QueryCard x={qx} y={qy} style={qStyle} typed={f < qIn ? undefined : typed} caret={caret} />
			<CompanyCard {...POS.card} kind="me" badge={{}} style={card(1)} />
			<CompanyCard {...POS.ghost1} kind="ghost" style={card(2)} />
			<CompanyCard {...POS.ghost2} kind="ghost" style={card(3)} />
			<HeadlineA wordStyle={word} plateStyle={plate} glow={glow} subStyle={sub} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V03
 * 2.5D parallax: layers at different depths under a slow camera orbit. Seamless loop. */
export const V03_D = 240;
export const V03: React.FC = () => {
	const f = useCurrentFrame();
	const D = V03_D;
	const cx = wave(f, D); // camera x
	const cy = wave(f, D, 0.25); // camera y
	const depth = (d: number): CSSProperties => ({transform: `translate(${cx * d * 16}px, ${cy * d * 5}px)`});
	return (
		<Scene f={f} period={D} amp={1.4}>
			<div style={{position: 'absolute', inset: 0, ...depth(0.25)}}>
				<HeadlineA glow={1 + 0.08 * cy} />
			</div>
			<div style={{position: 'absolute', inset: 0, ...depth(1)}}>
				<Mascot {...POS.mascot} lift={3 + 3 * cy} rotate={cx * 0.8} scale={1 + 0.008 * cy} />
			</div>
			<div style={{position: 'absolute', inset: 0, perspective: 1100, perspectiveOrigin: '1330px 200px'}}>
				<div style={{position: 'absolute', inset: 0, transformStyle: 'preserve-3d', transformOrigin: '1330px 200px', transform: `translate(${cx * 9}px, ${cy * 3}px) rotateY(${-cx * 5}deg) rotateX(${cy * 1.5}deg)`}}>
					<CardStack styles={(i) => ({transform: `translateZ(${[24, 12, 0, -8][i]}px)`})} />
				</div>
			</div>
		</Scene>
	);
};

/* ---------------------------------------------------------------- V04
 * Card choreography: "Jūsų įmonė" climbs from last place to first, then earns the badge. */
export const V04_D = 240;
export const V04: React.FC = () => {
	const f = useCurrentFrame();
	const D = V04_D;
	const top = POS.card.y;
	const gap = 10;
	// slots in "before" order [ghost1, ghost2, me] and "after" order [me, ghost1, ghost2]
	const before = {g1: top, g2: top + GHOST_H + gap, me: top + 2 * (GHOST_H + gap)};
	const after = {me: top, g1: top + CARD_H + gap, g2: top + CARD_H + gap + GHOST_H + gap};
	const inAt = BUILD + 2;
	const swap = 70;
	const sMe = sp(f, swap, {damping: 22, stiffness: 80, mass: 1});
	const sG1 = sp(f, swap + 5, {damping: 200, stiffness: 90});
	const sG2 = sp(f, swap + 9, {damping: 200, stiffness: 90});
	const isBefore = f >= inAt;
	const yMe = isBefore ? mix(before.me, after.me, sMe) : after.me;
	const yG1 = isBefore ? mix(before.g1, after.g1, sG1) : after.g1;
	const yG2 = isBefore ? mix(before.g2, after.g2, sG2) : after.g2;
	const flight = Math.sin(Math.min(1, sMe) * Math.PI) * (f >= swap ? 1 : 0); // 0..1..0 while climbing
	const enter = (i: number) => restage(f, inAt + i * 5, i, 16);
	// ghosts step aside while the company card passes
	const makeWay = (sv: number) => (f >= swap ? Math.sin(Math.min(1, sv) * Math.PI) * 14 : 0);
	const meStyle: CSSProperties = {
		...enter(2),
		...(f >= inAt
			? {
					transform: `${enter(2).transform ?? ''} translateX(${-flight * 14}px) scale(${1 + flight * 0.03})`,
					opacity: Number(enter(2).opacity ?? 1) * mix(0.82, 1, prog(f, swap - 4, 16)),
					zIndex: 5,
				}
			: {}),
	};
	const badgeAt = swap + 30;
	const badge: CSSProperties | null =
		f < inAt
			? exitStyle(exitP(f, 2))
			: f < badgeAt
				? null
				: {opacity: prog(f, badgeAt, 8), transform: `scale(${mix(0.5, 1, sp(f, badgeAt, LIVELY))})`, transformOrigin: '50% 50%'};
	const glow = f >= badgeAt ? prog(f, badgeAt, 10) * (1 - prog(f, badgeAt + 14, 30, easeInOut)) : 0;
	return (
		<Scene f={f} period={D}>
			<HeadlineA />
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} />
			<QueryCard {...POS.query} style={enter(0)} />
			<CompanyCard x={POS.card.x + makeWay(sG1)} y={yG1} kind="ghost" style={enter(0)} />
			<CompanyCard x={POS.card.x + makeWay(sG2)} y={yG2} kind="ghost" style={enter(1)} />
			<CompanyCard x={POS.card.x} y={yMe} kind="me" badge={badge} style={meStyle} glow={glow} />
		</Scene>
	);
};

/* ---------------------------------------------------------------- V05
 * Lights dim, a soft spotlight reads the headline, then the scene lights up. */
export const V05_D = 240;
export const V05: React.FC = () => {
	const f = useCurrentFrame();
	const D = V05_D;
	const dimIn = prog(f, 6, 14, easeInOut);
	const sweepA = 22;
	const sweepB = 104;
	const t = prog(f, sweepA, sweepB - sweepA, easeInOut);
	// path: along line 1, then down to line 2 and the AI plate
	const px = t < 0.55 ? mix(40, 700, t / 0.55) : mix(700, 560, (t - 0.55) / 0.45);
	const py = t < 0.55 ? mix(105, 118, t / 0.55) : mix(118, 215, (t - 0.55) / 0.45);
	const lightUp = prog(f, sweepB - 6, 30, easeInOut);
	const R = mix(200, 1900, lightUp);
	const dark = 0.74 * dimIn * (1 - lightUp);
	const glow = 1 + 0.6 * prog(f, sweepB - 20, 14) * (1 - prog(f, sweepB + 8, 40, easeInOut));
	const glint = prog(f, sweepB + 8, 34, easeInOut);
	return (
		<Scene f={f} period={D}>
			<Mascot {...POS.mascot} lift={3 + 3 * wave(f, D / 2)} glint={glint} />
			<CardStack />
			<HeadlineA glow={glow} />
			{dark > 0.001 ? (
				<div
					style={{
						position: 'absolute',
						inset: 0,
						background: `radial-gradient(circle ${R}px at ${px}px ${py}px, rgba(4,22,16,0) 0%, rgba(4,22,16,0) 45%, rgba(4,22,16,${dark}) 100%)`,
					}}
				/>
			) : null}
		</Scene>
	);
};
