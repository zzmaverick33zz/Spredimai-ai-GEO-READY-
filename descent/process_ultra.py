#!/usr/bin/env python3
"""Cuts the ultra-quality client videos (source-media/ultra/*.mp4, 1080p) into slot clips and posters.
Writes descent/media/<slot>-<name>.{webm,mp4} (+ -poster.webp) and a '-lite' mp4 (used by the single-file build).
Times are seconds in the source (see MEDIA_MAP.md). Run: python3 descent/process_ultra.py"""
import os, subprocess, json, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f'{R}/source-media/ultra'; OUT = f'{R}/descent/media'
ASPECT = {'16:9': (16, 9), '4:5': (4, 5), '1:1': (1, 1), '21:9': (21, 9), '9:16': (9, 16), '16:10': (16, 10)}
# size per aspect: (full width, lite width)
W = {'16:9': (1280, 800), '4:5': (720, 480), '1:1': (720, 480), '21:9': (1440, 840), '9:16': (540, 360), '16:10': (1200, 720)}
# slot name, file, start, duration, aspect, crop focus x (0..1), grade filter
CLIPS = [
 ('s01-hero',     'Discovery.mp4',  43.0, 8.0, '16:9', .5, 'eq=contrast=1.04:saturation=0.95'),
 ('s03-dive',     'Discovery.mp4',  38.0, 4.0, '4:5',  .55, 'eq=contrast=1.04'),
 ('s04-detail',   'Discovery.mp4',  68.0, 3.0, '1:1',  .5, 'eq=contrast=1.03'),
 ('s05-lift',     'Discovery.mp4',  63.0, 6.0, '16:9', .5, 'eq=contrast=1.04'),
 ('s05-lift-9x16','Discovery.mp4',  63.0, 6.0, '9:16', .5, 'eq=contrast=1.04'),
 ('s11-grain',    'Discovery.mp4',  71.0, 3.0, '1:1',  .5, 'eq=contrast=1.05'),
 ('s10-hands',    'WIDE BOARD.mp4', 18.6, 3.4, '4:5',  .7, 'eq=saturation=1.02'),
 ('s12-fitted',   'WIDE BOARD.mp4', 40.0, 4.0, '16:10', .5, 'eq=saturation=1.02'),
 ('s13-home',     'ANTAKALNIS_INTERJERAS.mp4', 1.0, 7.0, '21:9', .5, 'eq=contrast=1.03'),
]
STILLS = [   # slot name, file, time, aspect
 ('s02-fallen', 'Discovery.mp4', 14.6, '4:5', .55),
 ('s20-floors', 'GUOBA.mp4', 21.0, '4:5', .62),
 ('s21-stairs', 'ANTAKALNIS_LAIPTAI.mp4', 3.4, '4:5', .5),
]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def crop(asp, fx):
    a, b = ASPECT[asp]; return f"crop='if(gt(iw/ih,{a}/{b}),ih*{a}/{b},iw)':'if(gt(iw/ih,{a}/{b}),ih,iw*{b}/{a})':'(iw-ow)*{fx}':'(ih-oh)*0.5'"
only = set(sys.argv[1:])
for name, f, t0, dur, asp, fx, grade in CLIPS:
    if only and name not in only: continue
    full, lite = W[asp]
    for tag, w, crf in (('', full, 31), ('-lite', lite, 36)):
        vf = f"{crop(asp, fx)},scale={w}:-2:flags=lanczos,{grade},fps=25,format=yuv420p"
        sh('ffmpeg', '-y', '-ss', str(t0), '-t', str(dur), '-i', f'{SRC}/{f}', '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{name}{tag}.mp4')
        if not tag: sh('ffmpeg', '-y', '-ss', str(t0), '-t', str(dur), '-i', f'{SRC}/{f}', '-an', '-vf', vf, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '37', '-row-mt', '1', f'{OUT}/{name}.webm')
    sh('ffmpeg', '-y', '-ss', str(t0 + dur * 0.5), '-i', f'{SRC}/{f}', '-frames:v', '1', '-vf', f"{crop(asp, fx)},scale={full}:-2:flags=lanczos,{grade}", '-c:v', 'libwebp', '-quality', '78', f'{OUT}/{name}-poster.webp')
    print(name, [round(os.path.getsize(f'{OUT}/{name}{x}')/1e6, 2) for x in ('.mp4', '.webm', '-lite.mp4')], 'MB')
for name, f, t, asp, fx in STILLS:
    if only and name not in only: continue
    full, lite = W[asp]
    for tag, w in (('', int(full * 1.4)), ('-lite', full)):
        sh('ffmpeg', '-y', '-ss', str(t), '-i', f'{SRC}/{f}', '-frames:v', '1', '-vf', f"{crop(asp, fx)},scale={w}:-2:flags=lanczos", '-c:v', 'libwebp', '-quality', '80', f'{OUT}/{name}{tag}.webp')
    print(name, round(os.path.getsize(f'{OUT}/{name}.webp')/1e3), 'KB')
