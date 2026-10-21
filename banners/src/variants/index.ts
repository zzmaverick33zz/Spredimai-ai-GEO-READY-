import React from 'react';
import {V01, V01_D, V02, V02_D, V03, V03_D, V04, V04_D, V05, V05_D} from './A1';
import {V11, V11_D, V12, V12_D, V14, V14_D} from './A2';
import {V16, V16_D, V17, V17_D, V18, V18_D, V19, V19_D, V20, V20_D, V21, V21_D, V22, V22_D} from './C1';
import {V06, V06_D, V07, V07_D, V08, V08_D, V09, V09_D, V10, V10_D, V13, V13_D, V15, V15_D} from './B1';

/** keys: frames worth inspecting besides 0/25/50/75/100 % */
export type Variant = {id: string; slug: string; frames: number; component: React.FC; keys: number[]; contact: number[]};
export const VARIANTS: Variant[] = [
	{id: 'v01', slug: 'mask-reveal', component: V01, frames: V01_D, keys: [12, 26, 34, 40, 50, 64], contact: [0, 28, 44, 209]},
	{id: 'v02', slug: 'query-typing', component: V02, frames: V02_D, keys: [14, 30, 60, 90, 104, 122, 140], contact: [0, 60, 120, 269]},
	{id: 'v03', slug: 'parallax-2-5d', component: V03, frames: V03_D, keys: [30, 90, 150, 210], contact: [0, 60, 180, 239]},
	{id: 'v04', slug: 'cards-reorder', component: V04, frames: V04_D, keys: [14, 34, 70, 80, 88, 100, 106, 124], contact: [0, 50, 84, 239]},
	{id: 'v05', slug: 'spotlight', component: V05, frames: V05_D, keys: [14, 30, 50, 70, 90, 104, 116, 130], contact: [0, 50, 90, 239]},
	{id: 'v06', slug: 'question-typing', component: V06, frames: V06_D, keys: [14, 40, 60, 84, 96, 112, 126, 150], contact: [0, 50, 104, 269]},
	{id: 'v07', slug: 'badge-transfer', component: V07, frames: V07_D, keys: [14, 40, 76, 88, 96, 108, 124, 140], contact: [0, 60, 96, 269]},
	{id: 'v08', slug: 'cta-liquid-glass', component: V08, frames: V08_D, keys: [14, 24, 30, 54, 60, 74, 140, 150], contact: [0, 28, 58, 209]},
	{id: 'v09', slug: 'mascot-glint', component: V09, frames: V09_D, keys: [14, 30, 36, 44, 166], contact: [0, 34, 166, 239]},
	{id: 'v10', slug: 'minimal', component: V10, frames: V10_D, keys: [80, 90], contact: [0, 60, 84, 179]},
	{id: 'v11', slug: 'loop-a-to-b', component: V11, frames: V11_D, keys: [44, 50, 58, 66, 80, 90, 150, 160, 170, 180, 194], contact: [0, 64, 120, 239]},
	{id: 'v12', slug: 'mascot-first', component: V12, frames: V12_D, keys: [14, 26, 34, 46, 54, 60, 70, 84], contact: [0, 34, 60, 239]},
	{id: 'v13', slug: 'dark-neon', component: V13, frames: V13_D, keys: [14, 24, 30, 46, 56, 70], contact: [0, 30, 56, 239]},
	{id: 'v14', slug: 'grid-caret', component: V14, frames: V14_D, keys: [14, 26, 34, 44, 52, 56, 60, 70, 84], contact: [0, 34, 60, 239]},
	{id: 'v15', slug: 'cascade-hold', component: V15, frames: V15_D, keys: [14, 26, 36, 46, 56, 66, 76, 90], contact: [0, 36, 60, 269]},
	{id: 'v16', slug: 'mascot-hop-in', component: V16, frames: V16_D, keys: [14, 22, 34, 44, 54, 62, 72, 78, 90, 110, 124], contact: [0, 34, 62, 269]},
	{id: 'v17', slug: 'mascot-reads-along', component: V17, frames: V17_D, keys: [14, 26, 38, 50, 58, 70, 84, 96, 112, 126, 130], contact: [0, 40, 96, 269]},
	{id: 'v18', slug: 'mascot-peek', component: V18, frames: V18_D, keys: [14, 26, 40, 50, 62, 76, 84, 90, 96, 106, 116, 130, 150], contact: [0, 50, 112, 239]},
	{id: 'v19', slug: 'mascot-mood', component: V19, frames: V19_D, keys: [14, 30, 52, 64, 74, 90, 128, 136, 140, 144, 148, 150, 160, 180], contact: [0, 80, 146, 299]},
	{id: 'v20', slug: 'mascot-nod', component: V20, frames: V20_D, keys: [14, 26, 34, 44, 54, 58, 62, 90, 98, 110, 130], contact: [0, 40, 62, 239]},
	{id: 'v21', slug: 'mascot-wake-dark', component: V21, frames: V21_D, keys: [14, 26, 40, 48, 60, 72, 84, 100, 120], contact: [0, 40, 72, 239]},
	{id: 'v22', slug: 'mascot-loop-a-b', component: V22, frames: V22_D, keys: [34, 50, 56, 62, 70, 76, 84, 110, 164, 172, 180, 188, 196, 206, 226], contact: [0, 62, 120, 275]},
];
