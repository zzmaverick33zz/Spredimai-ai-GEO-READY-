import React from 'react';
import {useCurrentFrame} from 'remotion';
import {CompanyCard, QueryCard} from '../lib/Cards';
import {CTA, HeadlineA, HeadlineB, Subtitle} from '../lib/Headlines';
import {Mascot} from '../lib/Mascot';
import {POS, Scene} from '../lib/Scene';

export const Cards: React.FC<{badge?: boolean}> = ({badge = true}) => (
	<>
		<QueryCard {...POS.query} />
		<CompanyCard {...POS.card} kind="me" badge={badge ? {} : null} />
		<CompanyCard {...POS.ghost1} kind="ghost" />
		<CompanyCard {...POS.ghost2} kind="ghost" />
	</>
);

export const TestA: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Scene f={f} period={240}>
			<Mascot {...POS.mascot} />
			<Cards />
			<HeadlineA />
		</Scene>
	);
};

export const TestB: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Scene f={f} period={240}>
			<Mascot {...POS.mascot} />
			<Cards />
			<HeadlineB />
			<Subtitle italic style={{position: 'absolute', left: 48, top: 246}} />
			<CTA />
		</Scene>
	);
};
