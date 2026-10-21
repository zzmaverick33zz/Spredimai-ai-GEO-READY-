import React, {CSSProperties} from 'react';
import {Img, staticFile} from 'remotion';
import {clamp} from './anim';

export const MASCOT_W = 333;
export const MASCOT_H = 343;

type Props = {
	x: number; // left at scale 1
	y: number; // top at scale 1
	scale?: number;
	lift?: number; // px upward (bob); shadow reacts
	rotate?: number; // deg, pivots at the feet
	glint?: number; // 0..1 sweep progress, <=0 or >=1 = off
	glintStrength?: number;
	style?: CSSProperties; // entrance/exit (opacity, transform, filter) on the whole group
	shadow?: number; // shadow opacity multiplier
};

/** The only raster element: the glass mascot cut from banner-2. Contact shadow is drawn in code. */
export const Mascot: React.FC<Props> = ({x, y, scale = 1, lift = 0, rotate = 0, glint = -1, glintStrength = 0.55, style, shadow = 1}) => {
	const src = staticFile('mascot.png');
	const lh = clamp(lift / 30, -1, 1);
	const showGlint = glint > 0 && glint < 1;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: MASCOT_W, height: MASCOT_H, transformOrigin: '50% 96%', ...style}}>
			<div style={{position: 'absolute', inset: 0, transform: `scale(${scale})`, transformOrigin: '50% 96%'}}>
				{/* contact shadow */}
				<div
					style={{
						position: 'absolute',
						left: 30 + lh * 14,
						right: 18 + lh * 14,
						top: 300,
						height: 46,
						borderRadius: '50%',
						background: 'radial-gradient(closest-side, rgba(8,40,30,0.55), rgba(8,40,30,0.25) 60%, rgba(8,40,30,0) 100%)',
						opacity: shadow * (1 - lh * 0.35),
						filter: 'blur(4px)',
					}}
				/>
				<div style={{position: 'absolute', inset: 0, transform: `translateY(${-lift}px) rotate(${rotate}deg)`, transformOrigin: '50% 96%'}}>
					<Img src={src} style={{position: 'absolute', inset: 0, width: MASCOT_W, height: MASCOT_H}} />
					{showGlint ? (
						<div
							style={{
								position: 'absolute',
								inset: 0,
								WebkitMaskImage: `url(${src})`,
								WebkitMaskSize: '100% 100%',
								maskImage: `url(${src})`,
								maskSize: '100% 100%',
								background: `linear-gradient(115deg, rgba(255,255,255,0) ${glint * 160 - 40}%, rgba(255,255,255,${glintStrength}) ${glint * 160 - 22}%, rgba(255,255,255,0) ${glint * 160 - 4}%)`,
								mixBlendMode: 'screen',
							}}
						/>
					) : null}
				</div>
			</div>
		</div>
	);
};
