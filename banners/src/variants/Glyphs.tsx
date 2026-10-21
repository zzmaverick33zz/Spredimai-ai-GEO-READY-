import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BODY, HEAD} from '../lib/fonts';

const S = 'ū ų į ė š ž č ą ę  Ū Ų Į Ė Š Ž Č Ą Ę';
export const Glyphs: React.FC = () => (
	<AbsoluteFill style={{background: '#F4FBF8', padding: 30, gap: 14, color: '#0B1F18'}}>
		<div style={{fontFamily: HEAD, fontWeight: 700, fontSize: 56}}>{S}</div>
		<div style={{fontFamily: HEAD, fontWeight: 600, fontSize: 40}}>Lexend 600: {S}</div>
		<div style={{fontFamily: BODY, fontWeight: 500, fontSize: 36}}>Roboto 500: {S}</div>
		<div style={{fontFamily: BODY, fontStyle: 'italic', fontSize: 36}}>Roboto italic: {S}</div>
	</AbsoluteFill>
);
