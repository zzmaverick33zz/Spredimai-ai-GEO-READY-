import React, {CSSProperties} from 'react';
import {CompanyCard, QueryCard} from '../lib/Cards';
import {POS} from '../lib/Scene';

/** The source card stack: query, "Jūsų įmonė" + badge, two ghost cards. */
export const CardStack: React.FC<{
	styles?: (i: number) => CSSProperties | undefined; // 0 query, 1 me, 2 ghost1, 3 ghost2
	badge?: CSSProperties | null;
	theme?: 'light' | 'dark';
	glow?: number;
}> = ({styles, badge = {}, theme, glow}) => (
	<>
		<QueryCard {...POS.query} theme={theme} style={styles?.(0)} />
		<CompanyCard {...POS.card} kind="me" badge={badge} theme={theme} style={styles?.(1)} glow={glow} />
		<CompanyCard {...POS.ghost1} kind="ghost" theme={theme} style={styles?.(2)} />
		<CompanyCard {...POS.ghost2} kind="ghost" theme={theme} style={styles?.(3)} />
	</>
);

export const B_SUB_POS = {left: 48, top: 246};
export const A_SUB_TOP = 287;
