#!/usr/bin/env python3
"""Scene loops for 'The descent' (studio build). Every piece is ONE cut-free shot of the client's Discovery film (cut list from ffmpeg scene
detection; the film changes shot every ~1-2.5 s). A scene is one piece, or a short sequence of pieces joined with dissolves (to tell a process
like "the trunk comes out of the water"), slowed down where short, then made into a seamless loop (cross-fade of the end into the start,
or boomerang for textures). Encodes hd (1920) / sd (1280) / webm / poster.
Run: python3 studio/process_scenes.py [scene names]  (needs source-media/ultra/Discovery.mp4)"""
import os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = f'{R}/source-media/ultra/Discovery.mp4'; OUT = f'{R}/studio/media'
TMP = '/tmp/claude-0/scenes_studio'; os.makedirs(TMP, exist_ok=True)
DISS = 0.4   # dissolve between pieces of a sequence
# name, [(start, length, slow-motion factor), ...], loop mode, cross-fade seconds
SCENES = [
 ('d1-lake',   [(0.4, 3.0, 1)], 'pp', 0),
 ('d3-divers', [(21.12, 2.3, 2)], 'xf', 0.9),                                  # suiting up
 ('d4-water',  [(33.52, 2.4, 2)], 'xf', 1.0),                                  # the diver slips under the surface
 ('d5-trunk',  [(43.58, 2.35, 2)], 'pp', 0),                                   # a trunk on the lake bed
 ('d6-line',   [(58.5, 1.0, 2.5), (59.7, 1.0, 2.5)], 'xf', 0.7),               # the line goes on
 ('d7-lift',   [(63.55, 1.1, 2), (64.78, 1.1, 2), (66.08, 1.1, 2)], 'xf', 0.8), # the trunk comes out of the water
 ('d8-wood',   [(71.12, 1.2, 2)], 'pp', 0),                                    # black wood, close
]
if len(sys.argv) > 1: SCENES = [s for s in SCENES if s[0] in sys.argv[1:]]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def piece(n, i, s, d, slow):
    p = f'{TMP}/{n}-p{i}.mp4'; vf = 'scale=1920:-2:flags=lanczos,fps=25'
    if slow > 1: vf += f',setpts={slow}*PTS,minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:vsbmc=1'
    sh('ffmpeg', '-y', '-ss', str(s), '-t', str(d), '-i', SRC, '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', p); return p
for n, pcs, mode, F in SCENES:
    ps = [piece(n, i, *x) for i, x in enumerate(pcs)]
    base = ps[0]
    if len(ps) > 1:                                                          # join the pieces with dissolves
        cur = ps[0]
        for i, nxt in enumerate(ps[1:], 1):
            out = f'{TMP}/{n}-j{i}.mp4'; off = dur(cur) - DISS
            sh('ffmpeg', '-y', '-i', cur, '-i', nxt, '-filter_complex', f'[0:v][1:v]xfade=transition=fade:duration={DISS}:offset={off:.3f}[o]', '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', out); cur = out
        base = cur
    D = dur(base); loop = f'{TMP}/{n}-loop.mp4'
    if mode == 'pp': fc = '[0:v]split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1:a=0[o]'
    else: fc = (f'[0:v]split=3[a][b][c];[a]trim=start={F}:end={D - F},setpts=PTS-STARTPTS[mid];[b]trim=start={D - F}:end={D},setpts=PTS-STARTPTS[tail];'
                f'[c]trim=start=0:end={F},setpts=PTS-STARTPTS[head];[tail][head]xfade=transition=fade:duration={F}:offset=0[x];[x][mid]concat=n=2:v=1:a=0[o]')
    sh('ffmpeg', '-y', '-i', base, '-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', loop)
    L = dur(loop); sizes = []
    for w, crf, tag in ((1920, 25, 'hd'), (1280, 28, 'sd')):
        sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', f'scale={w}:-2:flags=lanczos,eq=contrast=1.04', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{n}-{tag}.mp4'); sizes.append(round(os.path.getsize(f'{OUT}/{n}-{tag}.mp4') / 1e6, 2))
    sh('ffmpeg', '-y', '-ss', str(L * .4), '-i', loop, '-frames:v', '1', '-vf', 'scale=1600:-2:flags=lanczos', '-c:v', 'libwebp', '-quality', '66', f'{OUT}/{n}-poster.webp')
    sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', 'scale=1280:-2:flags=lanczos,eq=contrast=1.04', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', f'{OUT}/{n}-hd.webm'); sizes.append(round(os.path.getsize(f'{OUT}/{n}-hd.webm') / 1e6, 2))
    print(n, f'loop {L:.1f}s', sizes, 'MB', flush=True)
