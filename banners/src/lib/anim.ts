import {CSSProperties} from 'react';
import {Easing, interpolate, spring} from 'remotion';

export const FPS = 30;
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const easeIn = Easing.bezier(0.55, 0, 1, 0.45);

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

/** eased 0..1 between start and start+dur */
export const prog = (f: number, start: number, dur: number, ease = easeOut) =>
	interpolate(f, [start, start + dur], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: ease,
	});

export type SpringCfg = {damping?: number; stiffness?: number; mass?: number};
export const SOFT: SpringCfg = {damping: 200, stiffness: 90, mass: 1}; // no overshoot
export const LIVELY: SpringCfg = {damping: 17, stiffness: 120, mass: 0.9}; // small overshoot
export const sp = (f: number, start: number, cfg: SpringCfg = SOFT) =>
	spring({frame: f - start, fps: FPS, config: cfg});

/* --- poster-first structure ------------------------------------------------
 * Frame 0 is the finished poster. Elements that get re-staged leave quickly
 * (EXIT_DUR, ease-in) and then enter on their own cue (slower, spring/ease-out).
 */
export const EXIT_AT = 8;
export const EXIT_DUR = 9;
export const BUILD = EXIT_AT + EXIT_DUR + 3; // first frame an entrance may start

/** 1 at poster, 0 after exit (stagger in frames) */
export const exitP = (f: number, stagger = 0) => 1 - prog(f, EXIT_AT + stagger, EXIT_DUR, easeIn);

export const exitStyle = (e: number): CSSProperties => ({
	opacity: e,
	transform: `translateY(${(1 - e) * -8}px)`,
	filter: e < 1 ? `blur(${(1 - e) * 4}px)` : undefined,
});

/** standard entrance: opacity + rise + de-blur (3 properties) */
export const riseStyle = (f: number, start: number, dist = 18, cfg: SpringCfg = SOFT): CSSProperties => {
	const s = sp(f, start, cfg);
	const o = prog(f, start, 12);
	return {
		opacity: o,
		transform: `translateY(${(1 - s) * dist}px)`,
		filter: o < 1 ? `blur(${(1 - o) * 6}px)` : undefined,
	};
};

/** poster -> exit -> entrance (rise) in one call */
export const restage = (f: number, enter: number, stagger = 0, dist = 18, cfg: SpringCfg = SOFT): CSSProperties =>
	f < enter ? exitStyle(exitP(f, stagger)) : riseStyle(f, enter, dist, cfg);

/** periodic offset that loops seamlessly over `period` frames */
export const wave = (f: number, period: number, phase = 0) => Math.sin(((f / period) + phase) * Math.PI * 2);
