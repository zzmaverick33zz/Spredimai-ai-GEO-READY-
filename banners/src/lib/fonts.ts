import {loadFont as loadLexend} from '@remotion/google-fonts/Lexend';
import {loadFont as loadRoboto} from '@remotion/google-fonts/Roboto';

const subsets: ('latin' | 'latin-ext')[] = ['latin', 'latin-ext'];
export const HEAD = loadLexend('normal', {weights: ['500', '600', '700'], subsets}).fontFamily;
export const BODY = loadRoboto('normal', {weights: ['400', '500'], subsets}).fontFamily;
loadRoboto('italic', {weights: ['400', '500'], subsets});
