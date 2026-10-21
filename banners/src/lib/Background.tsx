import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {wave} from './anim';

/** Source gradient (#52FFBA -> #315447) plus a soft drifting mesh. `period` keeps the drift loopable. */
export const Background: React.FC<{f: number; period: number; dark?: boolean; still?: boolean; amp?: number}> = ({
	f,
	period,
	dark,
	still,
	amp = 1,
}) => {
	const k = still ? 0 : amp;
	const a = wave(f, period) * k;
	const b = wave(f, period, 0.25) * k;
	if (dark) {
		return (
			<AbsoluteFill style={{background: 'linear-gradient(90deg, #0C2219 0%, #081712 55%, #050E0B 100%)'}}>
				<AbsoluteFill
					style={{
						background: `radial-gradient(520px 300px at ${300 + a * 30}px ${120 + b * 14}px, rgba(82,255,186,0.16), rgba(82,255,186,0) 70%),
						radial-gradient(420px 320px at ${930 + b * 24}px ${210 + a * 12}px, rgba(70,200,170,0.20), rgba(70,200,170,0) 70%),
						radial-gradient(520px 260px at ${1340 - a * 30}px ${190 - b * 10}px, rgba(82,255,186,0.10), rgba(82,255,186,0) 70%)`,
					}}
				/>
			</AbsoluteFill>
		);
	}
	return (
		<AbsoluteFill style={{background: 'linear-gradient(90deg, #52FFBA 0%, #315447 100%)'}}>
			<AbsoluteFill
				style={{
					background: `radial-gradient(640px 320px at ${180 + a * 40}px ${70 + b * 20}px, rgba(214,255,238,0.30), rgba(214,255,238,0) 70%),
					radial-gradient(460px 360px at ${930 + b * 30}px ${200 + a * 16}px, rgba(150,255,215,0.22), rgba(150,255,215,0) 70%),
					radial-gradient(620px 300px at ${1420 - a * 40}px ${360 - b * 16}px, rgba(18,52,42,0.45), rgba(18,52,42,0) 72%),
					radial-gradient(520px 260px at ${560 - b * 30}px ${420 + a * 10}px, rgba(30,120,90,0.18), rgba(30,120,90,0) 70%)`,
				}}
			/>
		</AbsoluteFill>
	);
};

/** Static grain + vignette, always the top layer. Static so it never shimmers. */
export const Overlay: React.FC<{dark?: boolean}> = ({dark}) => (
	<>
		<AbsoluteFill
			style={{
				backgroundImage: `url(${staticFile('grain.png')})`,
				backgroundSize: '256px 256px',
				mixBlendMode: 'overlay',
				opacity: dark ? 0.10 : 0.08,
				pointerEvents: 'none',
			}}
		/>
		<AbsoluteFill
			style={{
				background: dark
					? 'radial-gradient(ellipse 75% 95% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)'
					: 'radial-gradient(ellipse 80% 110% at 45% 50%, rgba(0,0,0,0) 60%, rgba(4,30,22,0.22) 100%)',
				pointerEvents: 'none',
			}}
		/>
	</>
);
