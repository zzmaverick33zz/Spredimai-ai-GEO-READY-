import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Background, Overlay} from './Background';
import './fonts';

export const W = 1584;
export const H = 396;

/** Default positions shared by all variants (px, 1584x396). */
export const POS = {
	mascot: {x: 772, y: 24},
	query: {x: 1098, y: 44},
	card: {x: 1110, y: 126},
	ghost1: {x: 1110, y: 224},
	ghost2: {x: 1110, y: 292},
};

export const Scene: React.FC<{f: number; period: number; dark?: boolean; still?: boolean; amp?: number; children: React.ReactNode}> = ({f, period, dark, still, amp, children}) => (
	<AbsoluteFill style={{overflow: 'hidden', background: dark ? '#06110E' : '#3E9E7C'}}>
		<Background f={f} period={period} dark={dark} still={still} amp={amp} />
		{children}
		<Overlay dark={dark} />
	</AbsoluteFill>
);
