import React, {CSSProperties} from 'react';
import {mix} from './anim';
import {BODY, HEAD} from './fonts';

export const A_LINES = ['Jūsų klientai jau', 'renkasi per'];
export const AI = 'AI';
export const B_LINES = ['ChatGPT rekomenduoja', 'jūsų konkurentus,', 'o ne jus?'];
export const SUB = 'GEO OPTIMIZAVIMAS ĮMONĖMS LIETUVOJE';
export const CTA_TEXT = 'Sužinokite, ar ChatGPT rekomenduoja jus';

type WS = (line: number, word: number, gi: number) => CSSProperties | undefined;

/** Renders a line as words; `typedLeft` chars of this line visible (Infinity = all). */
const Words: React.FC<{text: string; line: number; giStart: number; wordStyle?: WS; typedLeft?: number}> = ({text, line, giStart, wordStyle, typedLeft = Infinity}) => {
	const words = text.split(' ');
	let used = 0;
	return (
		<>
			{words.map((w, i) => {
				const visible = Math.max(0, Math.min(w.length, typedLeft - used));
				used += w.length + 1;
				const shown = typedLeft === Infinity ? w : w.slice(0, visible);
				return (
					<React.Fragment key={i}>
						<span style={{display: 'inline-block', whiteSpace: 'pre', ...(wordStyle?.(line, i, giStart + i) ?? {})}}>
							{shown}
							{/* keep layout stable while typing: invisible remainder */}
							{typedLeft !== Infinity && visible < w.length ? <span style={{visibility: 'hidden'}}>{w.slice(visible)}</span> : null}
						</span>
						{i < words.length - 1 ? ' ' : null}
					</React.Fragment>
				);
			})}
		</>
	);
};

/* Mask lines need room for Lithuanian marks: macron above (ū), ogonek below (ų, į). */
const MASK_PAD_TOP = 0.16;
const MASK_PAD_BOTTOM = 0.26;

type LineOpts = {
	mask?: boolean;
	lineStyle?: (line: number) => CSSProperties | undefined;
	innerStyle?: (line: number) => CSSProperties | undefined;
};

const Line: React.FC<{i: number; size: number; children: React.ReactNode; style?: CSSProperties} & LineOpts> = ({i, size, children, mask, lineStyle, innerStyle, style}) => (
	<div
		style={{
			position: 'relative',
			overflow: mask ? 'hidden' : undefined,
			paddingTop: mask ? size * MASK_PAD_TOP : 0,
			paddingBottom: mask ? size * MASK_PAD_BOTTOM : 0,
			marginTop: mask ? -size * MASK_PAD_TOP : 0,
			marginBottom: mask ? -size * MASK_PAD_BOTTOM : 0,
			...style,
			...(lineStyle?.(i) ?? {}),
		}}
	>
		<div style={{...(innerStyle?.(i) ?? {})}}>{children}</div>
	</div>
);

export type AIPlateProps = {
	plateStyle?: CSSProperties;
	aiStyle?: CSSProperties;
	glow?: number; // 0..~1.3
	aiTyped?: number; // 0..2 characters
	caret?: number; // caret opacity after AI
	theme?: 'light' | 'dark';
};

/**
 * White "AI" measured 2.3-2.8:1 on the mint gradient (fails 3:1), so it sits on a
 * deep-green glass plate (white on #0F3226 ~ 12:1).
 */
export const AIPlate: React.FC<AIPlateProps & {size: number}> = ({size, plateStyle, aiStyle, glow = 1, aiTyped, caret = 0}) => {
	const shown = aiTyped === undefined ? AI : AI.slice(0, Math.floor(aiTyped));
	return (
		<div
			style={{
				position: 'relative',
				display: 'inline-flex',
				alignItems: 'center',
				height: size * 1.04,
				padding: `0 ${size * 0.17}px`,
				borderRadius: size * 0.2,
				background: 'linear-gradient(160deg, #164637 0%, #0D2C22 55%, #0A231B 100%)',
				border: '1px solid rgba(130,255,205,0.35)',
				boxShadow: `0 18px 40px rgba(4,36,26,0.35), inset 0 1px 0 rgba(200,255,232,0.35), 0 0 ${40 * glow}px rgba(82,255,186,${0.35 * glow})`,
				boxSizing: 'border-box',
				...plateStyle,
			}}
		>
			<span
				style={{
					fontFamily: HEAD,
					fontWeight: 700,
					fontSize: size,
					lineHeight: 1,
					letterSpacing: '-0.02em',
					color: '#FFFFFF',
					textShadow: `0 0 ${18 * glow}px rgba(82,255,186,${0.75 * Math.min(glow, 1.3)}), 0 0 ${48 * glow}px rgba(82,255,186,${0.4 * Math.min(glow, 1.3)})`,
					position: 'relative',
					top: size * 0.02,
					whiteSpace: 'pre',
					...aiStyle,
				}}
			>
				{shown}
				{aiTyped !== undefined && shown.length < 2 ? <span style={{visibility: 'hidden'}}>{AI.slice(shown.length)}</span> : null}
			</span>
			{caret > 0 ? (
				<span style={{position: 'absolute', right: size * 0.1, top: size * 0.2, width: 5, height: size * 0.66, borderRadius: 2, background: '#52FFBA', opacity: caret, boxShadow: '0 0 12px rgba(82,255,186,0.8)'}} />
			) : null}
		</div>
	);
};

export const Subtitle: React.FC<{style?: CSSProperties; italic?: boolean; color?: string; size?: number; spacing?: string}> = ({style, italic, color = '#0B1F18', size = 22, spacing}) => (
	<div
		style={{
			fontFamily: BODY,
			fontWeight: italic ? 400 : 500,
			fontStyle: italic ? 'italic' : 'normal',
			fontSize: size,
			letterSpacing: spacing ?? (italic ? '0.12em' : '0.06em'),
			color,
			whiteSpace: 'nowrap',
			...style,
		}}
	>
		{SUB}
	</div>
);

export const HeadlineA: React.FC<
	{
		x?: number;
		y?: number;
		size?: number;
		color?: string;
		wordStyle?: WS;
		subStyle?: CSSProperties;
		hideSub?: boolean;
		style?: CSSProperties;
		plateWrapStyle?: CSSProperties;
	} & LineOpts &
		AIPlateProps
> = ({x = 46, y = 52, size = 84, color = '#081A14', wordStyle, subStyle, hideSub, style, plateWrapStyle, mask, lineStyle, innerStyle, ...plate}) => (
	<div style={{position: 'absolute', left: x, top: y, fontFamily: HEAD, fontWeight: 700, fontSize: size, lineHeight: 1.06, letterSpacing: '-0.025em', color, ...style}}>
		<Line i={0} size={size} mask={mask} lineStyle={lineStyle} innerStyle={innerStyle}>
			<Words text={A_LINES[0]} line={0} giStart={0} wordStyle={wordStyle} />
		</Line>
		<div style={{display: 'flex', alignItems: 'flex-end', gap: size * 0.22, marginTop: size * 0.04}}>
			<Line i={1} size={size} mask={mask} lineStyle={lineStyle} innerStyle={innerStyle} style={{paddingBottom: (mask ? size * MASK_PAD_BOTTOM : 0) + size * 0.04}}>
				<Words text={A_LINES[1]} line={1} giStart={3} wordStyle={wordStyle} />
			</Line>
			<div style={{display: 'inline-block', ...plateWrapStyle}}>
				<AIPlate size={size * 1.32} {...plate} />
			</div>
		</div>
		{hideSub ? null : <Subtitle style={{marginTop: size * 0.32, ...subStyle}} />}
	</div>
);

export const HeadlineB: React.FC<
	{
		x?: number;
		y?: number;
		size?: number;
		color?: string;
		accent?: string; // colour for "o ne jus?"
		accentStyle?: CSSProperties;
		wordStyle?: WS;
		typed?: number; // characters across all three lines
		caret?: number;
		style?: CSSProperties;
	} & LineOpts
> = ({x = 46, y = 34, size = 60, color = '#081A14', accent, accentStyle, wordStyle, typed, caret = 0, style, mask, lineStyle, innerStyle}) => {
	let left = typed ?? Infinity;
	let gi = 0;
	// which line holds the caret
	let caretLine = -1;
	if (typed !== undefined) {
		let rem = typed;
		for (let i = 0; i < B_LINES.length; i++) {
			if (rem <= B_LINES[i].length) {
				caretLine = i;
				break;
			}
			rem -= B_LINES[i].length;
		}
		if (caretLine === -1) caretLine = B_LINES.length - 1;
	}
	return (
		<div style={{position: 'absolute', left: x, top: y, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', fontFamily: HEAD, fontWeight: 700, fontSize: size, lineHeight: 1.1, letterSpacing: '-0.02em', color, ...style}}>
			{/* flex column: mask lines use negative margins, which must not collapse */}
			{B_LINES.map((t, i) => {
				const tl = left;
				left = left === Infinity ? Infinity : Math.max(0, left - t.length);
				const g = gi;
				gi += t.split(' ').length;
				const isAccent = i === 2 && accent;
				const shownLen = tl === Infinity ? t.length : Math.min(t.length, tl);
				return (
					<Line key={i} i={i} size={size} mask={mask} lineStyle={lineStyle} innerStyle={innerStyle}>
						<span style={{position: 'relative', color: isAccent ? accent : undefined, ...(i === 2 ? accentStyle : {})}}>
							<Words text={t} line={i} giStart={g} wordStyle={wordStyle} typedLeft={tl === Infinity ? Infinity : tl} />
							{caret > 0 && caretLine === i ? (
								<Caret size={size} opacity={caret} offsetChars={t.length - shownLen} text={t} />
							) : null}
						</span>
					</Line>
				);
			})}
		</div>
	);
};

/** caret placed after the visible part of a typed line: measured with a hidden copy */
const Caret: React.FC<{size: number; opacity: number; offsetChars: number; text: string}> = ({size, opacity, offsetChars, text}) => (
	<span style={{position: 'absolute', left: 0, top: 0, whiteSpace: 'pre', pointerEvents: 'none'}}>
		<span style={{visibility: 'hidden'}}>{text.slice(0, text.length - offsetChars)}</span>
		<span style={{display: 'inline-block', width: Math.round(size * 0.06), height: size * 0.86, marginLeft: 3, verticalAlign: '-0.12em', background: '#0E3A2B', borderRadius: 2, opacity}} />
	</span>
);

/** CTA pill, liquid glass: masked iridescent rim, blurred translucent body, specular band, optional sheen sweep. */
export const CTA: React.FC<{
	x?: number;
	y?: number;
	style?: CSSProperties;
	shimmer?: number; // 0..1 sweep progress (off outside)
	hue?: number; // rim rotation, deg
	arrowX?: number;
	theme?: 'light' | 'dark';
	glow?: number;
}> = ({x = 46, y = 292, style, shimmer = -1, hue = 0, arrowX = 0, theme = 'light', glow = 0}) => {
	const dark = theme === 'dark';
	const on = shimmer > 0 && shimmer < 1;
	const RIM = 2.5;
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				height: 56,
				borderRadius: 28,
				boxShadow: dark
					? `0 0 ${22 + glow * 18}px rgba(82,255,186,${0.28 + glow * 0.2}), 0 10px 24px rgba(0,0,0,0.4)`
					: '0 12px 28px rgba(6,48,34,0.22), 0 2px 6px rgba(6,48,34,0.10)',
				...style,
			}}
		>
			{/* body */}
			<div
				style={{
					position: 'relative',
					height: '100%',
					borderRadius: 28,
					overflow: 'hidden',
					display: 'flex',
					alignItems: 'center',
					gap: 10,
					padding: '0 26px 0 30px',
					backdropFilter: 'blur(14px) saturate(1.4)',
					background: dark
						? 'linear-gradient(180deg, rgba(40,90,72,0.80) 0%, rgba(14,40,31,0.86) 100%)'
						: 'linear-gradient(180deg, rgba(255,255,255,0.80) 0%, rgba(246,255,251,0.62) 50%, rgba(226,250,240,0.55) 51%, rgba(240,255,249,0.70) 100%)',
					boxShadow: dark
						? 'inset 0 1px 0 rgba(160,255,215,0.35), inset 0 -8px 16px rgba(82,255,186,0.10)'
						: 'inset 0 2px 3px rgba(255,255,255,0.95), inset 0 -10px 16px rgba(150,225,200,0.35)',
				}}
			>
				<span style={{fontFamily: HEAD, fontWeight: 600, fontSize: 21, letterSpacing: '-0.005em', color: dark ? '#EFFFF8' : '#0B1F18', whiteSpace: 'nowrap', position: 'relative', zIndex: 2}}>
					{CTA_TEXT}
				</span>
				<svg width="22" height="22" viewBox="0 0 24 24" style={{transform: `translateX(${arrowX}px)`, position: 'relative', zIndex: 2}}>
					<path d="M4 12h15M13.5 6.5L19 12l-5.5 5.5" fill="none" stroke={dark ? '#52FFBA' : '#0B1F18'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
				</svg>
				{on ? (
					<div
						style={{
							position: 'absolute',
							top: -10,
							bottom: -10,
							left: `${mix(-30, 110, shimmer)}%`,
							width: '22%',
							transform: 'skewX(-24deg)',
							background: dark
								? 'linear-gradient(90deg, rgba(160,255,215,0) 0%, rgba(160,255,215,0.30) 50%, rgba(160,255,215,0) 100%)'
								: 'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 50%, rgba(255,255,255,0) 100%)',
							zIndex: 1,
						}}
					/>
				) : null}
			</div>
			{/* iridescent rim (masked ring) */}
			<div
				style={{
					position: 'absolute',
					inset: 0,
					borderRadius: 28,
					padding: RIM,
					background: dark
						? `conic-gradient(from ${hue}deg at 50% 50%, rgba(82,255,186,0.95), rgba(82,255,186,0.25), rgba(140,220,255,0.75), rgba(82,255,186,0.25), rgba(82,255,186,0.95))`
						: `conic-gradient(from ${hue}deg at 50% 50%, #ffffff, #b9e2ff, #f7c4ef, #fff0b5, #b8f7da, #c7d8ff, #ffffff)`,
					WebkitMask: 'linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)',
					WebkitMaskComposite: 'xor',
					maskComposite: 'exclude',
					pointerEvents: 'none',
				}}
			/>
		</div>
	);
};
