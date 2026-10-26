#!/usr/bin/env python3
"""Scene clips for 'The Descent' (natural-speed video, no scrubbing). hd = 1920 px for large screens, sd = 1280 px.
Run: python3 grand/process_scenes.py"""
import os, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = f'{R}/source-media/ultra/Discovery.mp4'; OUT = f'{R}/grand/media'
# each scene is ONE continuous shot (cuts found with ffmpeg scene detection were trimmed out); it plays once and holds its last frame
SCENES = [('d1-lake', 0.4, 2.9), ('d2-tree', 13.5, 2.4), ('d3-divers', 28.5, 2.3), ('d4-water', 36.0, 5.5), ('d5-trunk', 41.5, 6.0), ('d6-lift', 60.85, 2.5), ('d7-wood', 71.1, 2.7)]
import sys
if len(sys.argv) > 1: SCENES = [s for s in SCENES if s[0] in sys.argv[1:]]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for n, s, d in SCENES:
    for tag, w, crf in (('hd', 1920, 25), ('sd', 1280, 28)):
        sh('ffmpeg', '-y', '-ss', str(s), '-t', str(d), '-i', SRC, '-an', '-vf', f'scale={w}:-2:flags=lanczos,eq=contrast=1.04,fps=25,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{n}-{tag}.mp4')
    sh('ffmpeg', '-y', '-ss', str(s + d * .4), '-i', SRC, '-frames:v', '1', '-vf', 'scale=1600:-2:flags=lanczos', '-c:v', 'libwebp', '-quality', '66', f'{OUT}/{n}-poster.webp')
    sh('ffmpeg', '-y', '-ss', str(s), '-t', str(d), '-i', SRC, '-an', '-vf', 'scale=1280:-2:flags=lanczos,eq=contrast=1.04,fps=25,format=yuv420p', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', f'{OUT}/{n}-hd.webm')
    print(n, [round(os.path.getsize(f'{OUT}/{n}-{t}')/1e6, 2) for t in ('hd.mp4', 'sd.mp4', 'hd.webm')], 'MB', flush=True)
