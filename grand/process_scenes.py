#!/usr/bin/env python3
"""Seamless looping scene clips for 'The Descent'. Source shots are short (the film is edited with cuts every 2-3 s), so each scene is
ONE cut-free shot turned into a loop that has no visible jump:
  mode 'pp'   boomerang (forward, then backward): for landscapes and textures
  mode 'xf'   cross-fade loop: the last F seconds dissolve into the first F seconds: for shots with action
  speed 2     slow motion (frame interpolation) for shots that are too short
hd = 1920 px (large screens), sd = 1280 px, webm (VP9) fallback, poster.
Run: python3 grand/process_scenes.py [scene names]"""
import os, subprocess, sys, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = f'{R}/source-media/ultra/Discovery.mp4'; OUT = f'{R}/grand/media'
TMP = '/tmp/claude-0/scenes'; os.makedirs(TMP, exist_ok=True)
# name, start, length of the cut-free shot, slow-motion factor, loop mode, cross-fade seconds
SCENES = [('d1-lake', 0.4, 3.0, 1, 'pp', 0), ('d2-tree', 13.5, 2.45, 1, 'pp', 0), ('d3-divers', 21.05, 4.9, 1, 'xf', 0.8),
          ('d4-water', 36.2, 6.8, 1, 'xf', 1.0), ('d5-trunk', 43.6, 7.2, 1, 'xf', 1.0), ('d6-lift', 60.85, 2.5, 2, 'xf', 0.8), ('d7-wood', 71.05, 1.3, 2, 'pp', 0)]
if len(sys.argv) > 1: SCENES = [s for s in SCENES if s[0] in sys.argv[1:]]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
for n, s, d, speed, mode, F in SCENES:
    base = f'{TMP}/{n}-base.mp4'
    vf = 'scale=1920:-2:flags=lanczos,fps=25'
    if speed > 1: vf += f',setpts={speed}*PTS,minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:vsbmc=1'
    sh('ffmpeg', '-y', '-ss', str(s), '-t', str(d), '-i', SRC, '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', base)
    D = dur(base); loop = f'{TMP}/{n}-loop.mp4'
    if mode == 'pp':
        fc = '[0:v]split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1:a=0[o]'
    else:
        fc = (f'[0:v]split=3[a][b][c];[a]trim=start={F}:end={D - F},setpts=PTS-STARTPTS[mid];[b]trim=start={D - F}:end={D},setpts=PTS-STARTPTS[tail];'
              f'[c]trim=start=0:end={F},setpts=PTS-STARTPTS[head];[tail][head]xfade=transition=fade:duration={F}:offset=0[x];[x][mid]concat=n=2:v=1:a=0[o]')
    sh('ffmpeg', '-y', '-i', base, '-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', loop)
    L = dur(loop); sizes = []
    for w, crf, tag in ((1920, 25, 'hd'), (1280, 28, 'sd')):
        sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', f'scale={w}:-2:flags=lanczos,eq=contrast=1.04', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{n}-{tag}.mp4')
        sizes.append(round(os.path.getsize(f'{OUT}/{n}-{tag}.mp4') / 1e6, 2))
    sh('ffmpeg', '-y', '-ss', str(L * .4), '-i', loop, '-frames:v', '1', '-vf', 'scale=1600:-2:flags=lanczos', '-c:v', 'libwebp', '-quality', '66', f'{OUT}/{n}-poster.webp')
    sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', 'scale=1280:-2:flags=lanczos,eq=contrast=1.04', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', f'{OUT}/{n}-hd.webm')
    sizes.append(round(os.path.getsize(f'{OUT}/{n}-hd.webm') / 1e6, 2))
    print(n, f'loop {L:.1f}s', sizes, 'MB', flush=True)
