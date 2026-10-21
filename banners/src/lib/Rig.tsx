import React, {CSSProperties} from 'react';
import {Img, staticFile} from 'remotion';
import rig from '../../public/rig/rig.json';
import {clamp, easeInOut, prog, sp} from './anim';
import {MASCOT_H, MASCOT_W} from './Mascot';

/*
 * Rigged mascot: body (eyes + smile painted out by scripts/rig.py) with the original
 * eyes and smile as separate layers, so it can blink, look, smile and squash/stretch.
 * The little arm is fused with the glass body and is not separated.
 */

export type Pose = {
	lift?: number; // px up
	sx?: number; // squash/stretch about the feet
	sy?: number;
	tilt?: number; // deg, pivot at the feet
	dx?: number; // px offset
	lookX?: number; // -1..1 (eyes move ~5 px, smile ~3.5 px)
	lookY?: number; // -1..1
	blink?: number; // 0 open .. 1 closed
	smile?: number; // 1 = original; <1 flatter, >1 bigger
	eyes?: number; // eye scale (surprise > 1)
	glow?: number; // mint aura 0..1
	opacity?: number;
	style?: CSSProperties;
	clipBottom?: number; // y (in mascot px) below which the mascot is hidden (peeking)
};

type Feat = {x: number; y: number; w: number; h: number; cx: number; cy: number};
const F = rig as Record<'eye-l' | 'eye-r' | 'mouth', Feat>;

const Feature: React.FC<{name: keyof typeof F; dx: number; dy: number; sx: number; sy: number}> = ({name, dx, dy, sx, sy}) => {
	const f = F[name];
	return (
		<Img
			src={staticFile(`rig/${name}.png`)}
			style={{
				position: 'absolute',
				left: f.x,
				top: f.y,
				width: f.w,
				height: f.h,
				transformOrigin: `${f.cx - f.x}px ${f.cy - f.y}px`,
				transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`,
			}}
		/>
	);
};

export const RigMascot: React.FC<{x: number; y: number} & Pose> = ({
	x,
	y,
	lift = 0,
	sx = 1,
	sy = 1,
	tilt = 0,
	dx = 0,
	lookX = 0,
	lookY = 0,
	blink = 0,
	smile = 1,
	eyes = 1,
	glow = 0,
	opacity = 1,
	style,
	clipBottom,
}) => {
	const lh = clamp(lift / 40, -1, 1);
	const eyeSy = eyes * (1 - 0.92 * blink);
	return (
		<div style={{position: 'absolute', left: x + dx, top: y, width: MASCOT_W, height: MASCOT_H, opacity, ...style}}>
			{/* contact shadow: shrinks and fades as the mascot rises */}
			<div
				style={{
					position: 'absolute',
					left: 30 + lh * 30,
					right: 18 + lh * 30,
					top: 300,
					height: 46,
					borderRadius: '50%',
					background: 'radial-gradient(closest-side, rgba(8,40,30,0.55), rgba(8,40,30,0.25) 60%, rgba(8,40,30,0) 100%)',
					// hidden below the frame edge (peeking) -> no shadow
					opacity: (1 - lh * 0.6) * clamp(1 + lift / 60) * (clipBottom !== undefined ? 0 : 1),
					filter: 'blur(4px)',
					transform: `scaleX(${sx})`,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					transformOrigin: '50% 96%',
					transform: `translateY(${-lift}px) rotate(${tilt}deg) scale(${sx}, ${sy})`,
					clipPath: clipBottom !== undefined ? `inset(-40px -40px ${MASCOT_H - clipBottom + lift}px -40px)` : undefined,
					filter: glow > 0 ? `drop-shadow(0 0 ${18 * glow}px rgba(82,255,186,${0.55 * glow}))` : undefined,
				}}
			>
				<Img src={staticFile('rig/body.png')} style={{position: 'absolute', inset: 0, width: MASCOT_W, height: MASCOT_H}} />
				<Feature name="eye-l" dx={lookX * 5} dy={lookY * 4} sx={eyes} sy={eyeSy} />
				<Feature name="eye-r" dx={lookX * 4} dy={lookY * 4} sx={eyes} sy={eyeSy} />
				<Feature name="mouth" dx={lookX * 3.5} dy={lookY * 3} sx={0.8 + 0.2 * smile} sy={smile} />
			</div>
		</div>
	);
};

/* ---- motion primitives ---------------------------------------------------- */

/** blink centred at frame `at`: 0 -> 1 -> 0 over 7 frames */
export const blinkAt = (f: number, at: number) => {
	const c = prog(f, at - 3, 3, easeInOut);
	const o = prog(f, at, 4, easeInOut);
	return c * (1 - o);
};
export const blinks = (f: number, ats: number[]) => Math.max(0, ...ats.map((a) => blinkAt(f, a)));

/**
 * One hop: anticipation squash, stretched rise, parabolic arc, landing squash that
 * settles on a spring. Returns lift and scale. `start` = takeoff frame.
 */
export const hop = (f: number, start: number, air: number, height: number) => {
	const ant = prog(f, start - 5, 5, easeInOut) * (1 - prog(f, start, 2));
	const t = clamp((f - start) / air);
	const airborne = f >= start && f <= start + air;
	const lift = airborne ? height * 4 * t * (1 - t) : 0;
	const stretch = airborne ? 0.07 * Math.sin(Math.PI * t) * (t < 0.5 ? 1 : 0.5) : 0;
	const land = f > start + air ? 1 - sp(f, start + air, {damping: 9, stiffness: 200, mass: 0.6}) : 0;
	const squash = 0.09 * ant + 0.12 * land * (f > start + air ? 1 : 0);
	const sy = 1 + stretch - squash;
	const sx = 1 - stretch * 0.6 + squash * 0.7;
	return {lift, sx, sy, airborne, t};
};

/** combine several hops (non-overlapping) */
export const hops = (f: number, list: [number, number, number][]) => {
	let res = {lift: 0, sx: 1, sy: 1};
	for (const [s, a, h] of list) {
		const r = hop(f, s, a, h);
		res = {lift: res.lift + r.lift, sx: res.sx * r.sx, sy: res.sy * r.sy};
	}
	return res;
};
