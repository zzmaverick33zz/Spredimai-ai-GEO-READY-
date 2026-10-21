import React, {CSSProperties} from 'react';
import {Img, staticFile} from 'remotion';
import {BODY, HEAD} from './fonts';

export const QUERY = 'Geriausi sprendimai verslui Lietuvoje';
export const COMPANY = 'Jūsų įmonė';
export const BADGE = 'Rekomenduojama';

export type Theme = 'light' | 'dark';

const Building: React.FC<{size: number; color: string}> = ({size, color}) => (
	<svg width={size} height={size} viewBox="0 0 24 24" fill="none">
		<path d="M4 21V5.5A1.5 1.5 0 0 1 5.5 4h8A1.5 1.5 0 0 1 15 5.5V21" stroke={color} strokeWidth="1.6" strokeLinejoin="round" />
		<path d="M15 10h3.5A1.5 1.5 0 0 1 20 11.5V21" stroke={color} strokeWidth="1.6" strokeLinejoin="round" />
		<path d="M2.5 21h19" stroke={color} strokeWidth="1.6" strokeLinecap="round" />
		{[7.2, 11.8].map((x) => [7.5, 11, 14.5].map((y) => <rect key={`${x}-${y}`} x={x - 1} y={y - 1} width="2" height="2" rx="0.4" fill={color} />))}
		<rect x="8.4" y="17.5" width="2.2" height="3.5" rx="0.5" fill={color} />
		<rect x="16.6" y="13.5" width="1.8" height="1.8" rx="0.4" fill={color} />
		<rect x="16.6" y="17" width="1.8" height="1.8" rx="0.4" fill={color} />
	</svg>
);

export const Star: React.FC<{size: number; color?: string}> = ({size, color = '#fff'}) => (
	<svg width={size} height={size} viewBox="0 0 24 24">
		<path d="M12 2.8l2.75 5.9 6.45.75-4.78 4.4 1.3 6.37L12 17l-5.72 3.22 1.3-6.37L2.8 9.45l6.45-.75z" fill={color} />
	</svg>
);

/** ChatGPT query bubble. `typed` = number of characters shown (undefined = all). */
export const QueryCard: React.FC<{
	x: number;
	y: number;
	style?: CSSProperties;
	typed?: number;
	caret?: number; // caret opacity 0..1
	theme?: Theme;
}> = ({x, y, style, typed, caret = 0, theme = 'light'}) => {
	const dark = theme === 'dark';
	const text = typed === undefined ? QUERY : QUERY.slice(0, Math.max(0, Math.floor(typed)));
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				height: 60,
				width: 456,
				boxSizing: 'border-box',
				borderRadius: 30,
				padding: '0 18px 0 11px',
				display: 'flex',
				alignItems: 'center',
				gap: 12,
				background: dark ? 'rgba(18,40,33,0.78)' : 'rgba(255,255,255,0.94)',
				border: dark ? '1px solid rgba(82,255,186,0.28)' : '1px solid rgba(255,255,255,0.9)',
				boxShadow: dark ? '0 10px 30px rgba(0,0,0,0.45)' : '0 12px 30px rgba(6,48,34,0.20), inset 0 1px 0 rgba(255,255,255,0.9)',
				...style,
			}}
		>
			<Img src={staticFile('chatgpt-icon.png')} style={{width: 38, height: 38, flex: '0 0 38px'}} />
			<div style={{fontFamily: BODY, fontWeight: 400, fontSize: 20, color: dark ? '#E8F5EF' : '#24332D', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center'}}>
				<span>{text}</span>
				{caret > 0 ? (
					<span style={{display: 'inline-block', width: 2, height: 22, marginLeft: 2, background: dark ? '#52FFBA' : '#1E9E6E', opacity: caret}} />
				) : null}
			</div>
		</div>
	);
};

/** Badge pill. */
export const Badge: React.FC<{style?: CSSProperties; theme?: Theme}> = ({style, theme = 'light'}) => (
	<div
		style={{
			height: 34,
			padding: '0 13px 0 10px',
			borderRadius: 17,
			display: 'inline-flex',
			alignItems: 'center',
			gap: 5,
			background: theme === 'dark' ? '#52FFBA' : 'linear-gradient(180deg, #23B57D, #17996A)',
			color: theme === 'dark' ? '#06251A' : '#fff',
			fontFamily: BODY,
			fontWeight: 500,
			fontSize: 20,
			whiteSpace: 'nowrap',
			boxShadow: theme === 'dark' ? '0 0 18px rgba(82,255,186,0.45)' : '0 4px 10px rgba(10,90,60,0.25)',
			...style,
		}}
	>
		<Star size={17} color={theme === 'dark' ? '#06251A' : '#fff'} />
		{BADGE}
	</div>
);

const Bars: React.FC<{dark?: boolean; w1?: number; w2?: number; color?: string}> = ({w1 = 230, w2 = 160, color}) => (
	<div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
		<div style={{width: w1, height: 9, borderRadius: 5, background: color}} />
		<div style={{width: w2, height: 9, borderRadius: 5, background: color, opacity: 0.8}} />
	</div>
);

export const CARD_W = 444;
export const CARD_H = 84;
export const GHOST_H = 58;

/**
 * Company card. kind:
 *  'me'      white card, "Jūsų įmonė" + optional badge
 *  'rival'   white card with skeleton bars instead of a name (no invented names)
 *  'ghost'   translucent skeleton card (as in the source)
 */
export const CompanyCard: React.FC<{
	x: number;
	y: number;
	kind: 'me' | 'rival' | 'ghost';
	badge?: CSSProperties | null; // style for the badge, null = no badge
	style?: CSSProperties;
	theme?: Theme;
	height?: number;
	width?: number;
	glow?: number;
}> = ({x, y, kind, badge = null, style, theme = 'light', height, width = CARD_W, glow = 0}) => {
	const dark = theme === 'dark';
	const ghost = kind === 'ghost';
	const h = height ?? (ghost ? GHOST_H : CARD_H);
	const bg = ghost
		? dark
			? 'rgba(255,255,255,0.05)'
			: 'rgba(255,255,255,0.26)'
		: dark
			? 'rgba(20,44,36,0.86)'
			: 'rgba(255,255,255,0.97)';
	const icon = ghost ? (dark ? 'rgba(82,255,186,0.45)' : 'rgba(30,150,105,0.75)') : dark ? '#52FFBA' : '#1FA571';
	const tile = ghost ? 'transparent' : dark ? 'rgba(82,255,186,0.12)' : '#E3F6EE';
	const bar = ghost ? (dark ? 'rgba(255,255,255,0.14)' : 'rgba(255,255,255,0.45)') : dark ? 'rgba(255,255,255,0.18)' : '#DCE3E0';
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				width,
				height: h,
				boxSizing: 'border-box',
				borderRadius: ghost ? 10 : 14,
				background: bg,
				border: ghost
					? `1px solid ${dark ? 'rgba(82,255,186,0.14)' : 'rgba(255,255,255,0.35)'}`
					: `1px solid ${dark ? 'rgba(82,255,186,0.35)' : 'rgba(255,255,255,1)'}`,
				boxShadow: ghost
					? 'none'
					: dark
						? `0 14px 34px rgba(0,0,0,0.5), 0 0 ${24 * glow}px rgba(82,255,186,${0.35 * glow})`
						: `0 16px 36px rgba(6,48,34,${0.24 + glow * 0.1}), 0 0 0 ${glow * 2}px rgba(82,255,186,${0.6 * glow})`,
				display: 'flex',
				alignItems: 'center',
				padding: ghost ? '0 16px' : '0 16px 0 14px',
				gap: ghost ? 12 : 14,
				...style,
			}}
		>
			<div style={{width: ghost ? 34 : 54, height: ghost ? 34 : 54, borderRadius: 10, background: tile, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 'none'}}>
				<Building size={ghost ? 28 : 34} color={icon} />
			</div>
			{kind === 'me' ? (
				<div style={{display: 'flex', flexDirection: 'column', gap: 9, flex: 1}}>
					<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
						<span style={{fontFamily: HEAD, fontWeight: 600, fontSize: 22, color: dark ? '#F2FFF9' : '#10291F', whiteSpace: 'nowrap'}}>{COMPANY}</span>
						{badge ? <Badge theme={theme} style={badge} /> : null}
					</div>
					<Bars w1={210} w2={150} color={bar} />
				</div>
			) : kind === 'rival' ? (
				<div style={{display: 'flex', flexDirection: 'column', gap: 9, flex: 1}}>
					<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 34}}>
						<div style={{width: 128, height: 14, borderRadius: 7, background: dark ? 'rgba(255,255,255,0.3)' : '#B9C7C1'}} />
						{badge ? <Badge theme={theme} style={badge} /> : null}
					</div>
					<Bars w1={210} w2={150} color={bar} />
				</div>
			) : (
				<Bars w1={196} w2={130} color={bar} />
			)}
		</div>
	);
};
