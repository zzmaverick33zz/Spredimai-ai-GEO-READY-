import React from 'react';
import {Composition} from 'remotion';
import {H, W} from './lib/Scene';
import {TestA, TestB} from './variants/Test';
import {VARIANTS} from './variants';
import {Glyphs} from './variants/Glyphs';

export const Root: React.FC = () => (
	<>
		<Composition id="TestA" component={TestA} durationInFrames={30} fps={30} width={W} height={H} />
		<Composition id="TestB" component={TestB} durationInFrames={30} fps={30} width={W} height={H} />
		<Composition id="Glyphs" component={Glyphs} durationInFrames={1} fps={30} width={W} height={H} />
		{VARIANTS.map((v) => (
			<Composition key={v.id} id={v.id} component={v.component} durationInFrames={v.frames} fps={30} width={W} height={H} />
		))}
	</>
);
