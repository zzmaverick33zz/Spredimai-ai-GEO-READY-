#!/usr/bin/env python3
"""Final-quality cuts from the client's 1080p originals (source-media/ultra). Two tiers per clip:
  -hd  (viewports >= 1100 px): near-source resolution, crf 22
  -sd  (smaller screens / phones): ~960 px, crf 27
plus webm for the hd tier and a poster. The scroll-driven film is cut from several segments with a keyframe every 6 frames.
Run: python3 final/process_final.py [names...]"""
import os, subprocess, sys, tempfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f'{R}/source-media/ultra'; OUT = f'{R}/final/media'
ASP = {'16:9': (16, 9), '4:5': (4, 5), '1:1': (1, 1), '21:9': (21, 9), '9:16': (9, 16), '16:10': (16, 10)}
WD = {'16:9': (1920, 1280), '4:5': (1080, 720), '1:1': (1080, 720), '21:9': (1920, 1280), '9:16': (1080, 640), '16:10': (1600, 1024)}
CLIPS = [  # name, file, start, dur, aspect, focus-x
 ('s01-hero',      'Discovery.mp4', 43.0, 8.0, '16:9', .5),
 ('s03-dive',      'Discovery.mp4', 38.0, 4.0, '4:5', .55),
 ('s04-detail',    'Discovery.mp4', 68.0, 3.0, '1:1', .5),
 ('s05-lift',      'Discovery.mp4', 63.0, 6.0, '16:9', .5),
 ('s05-lift-9x16', 'Discovery.mp4', 63.0, 6.0, '9:16', .5),
 ('s11-grain',     'Discovery.mp4', 71.0, 3.0, '1:1', .5),
 ('s10-hands',     'WIDE BOARD.mp4', 18.6, 3.4, '4:5', .7),
 ('s12-fitted',    'WIDE BOARD.mp4', 40.0, 4.0, '16:10', .5),
 ('s13-home',      'ANTAKALNIS_INTERJERAS.mp4', 1.0, 7.0, '21:9', .5),
]
FILM = [('Discovery.mp4', s, d) for s, d in ((1.0, 2.5), (13.2, 2.5), (28.0, 2.0), (33.0, 2.0), (38.0, 3.0), (43.0, 4.0), (48.5, 2.0), (60.5, 2.0), (63.5, 2.5), (71.0, 2.0))]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def crop(asp, fx):
    a, b = ASP[asp]; return f"crop='if(gt(iw/ih,{a}/{b}),ih*{a}/{b},iw)':'if(gt(iw/ih,{a}/{b}),ih,iw*{b}/{a})':'(iw-ow)*{fx}':'(ih-oh)*0.5'"
GRADE = 'eq=contrast=1.04:saturation=1.0'
only = set(sys.argv[1:]); mb = lambda p: round(os.path.getsize(p) / 1e6, 2)
for name, f, t0, dur, asp, fx in CLIPS:
    if only and name not in only: continue
    for tag, w, crf in (('hd', WD[asp][0], 26), ('sd', WD[asp][1], 28)):
        vf = f"{crop(asp, fx)},scale={w}:-2:flags=lanczos,{GRADE},fps=25,format=yuv420p"
        sh('ffmpeg', '-y', '-ss', str(t0), '-t', str(dur), '-i', f'{SRC}/{f}', '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{name}-{tag}.mp4')
    sh('ffmpeg', '-y', '-ss', str(t0), '-t', str(dur), '-i', f'{SRC}/{f}', '-an', '-vf', f"{crop(asp, fx)},scale={WD[asp][0]}:-2:flags=lanczos,{GRADE},fps=25,format=yuv420p", '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '36', '-row-mt', '1', f'{OUT}/{name}-hd.webm')
    sh('ffmpeg', '-y', '-ss', str(t0 + dur * .5), '-i', f'{SRC}/{f}', '-frames:v', '1', '-vf', f"{crop(asp, fx)},scale={WD[asp][0]}:-2:flags=lanczos,{GRADE}", '-c:v', 'libwebp', '-quality', '82', f'{OUT}/{name}-poster.webp')
    print(name, 'hd', mb(f'{OUT}/{name}-hd.mp4'), 'sd', mb(f'{OUT}/{name}-sd.mp4'), 'webm', mb(f'{OUT}/{name}-hd.webm'), 'MB')
if not only or 'film' in only:
    tmp = tempfile.mkdtemp(); lst = []
    for i, (f, s, d) in enumerate(FILM):
        p = f'{tmp}/s{i}.mp4'
        sh('ffmpeg', '-y', '-ss', str(s), '-t', str(d), '-i', f'{SRC}/{f}', '-an', '-vf', f'scale=1920:1080:flags=lanczos,{GRADE},fps=25,format=yuv420p', '-c:v', 'libx264', '-preset', 'fast', '-crf', '10', p)
        lst.append(f"file '{p}'")
    open(f'{tmp}/l.txt', 'w').write('\n'.join(lst)); sh('ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/j.mp4')
    for tag, w, crf in (('hd', 1600, 29), ('sd', 1024, 29)):
        sh('ffmpeg', '-y', '-i', f'{tmp}/j.mp4', '-vf', f'scale={w}:-2:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-g', '8', '-keyint_min', '8', '-sc_threshold', '0', '-bf', '0', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{OUT}/film-{tag}.mp4')
    sh('ffmpeg', '-y', '-i', f'{tmp}/j.mp4', '-vf', 'scale=1280:-2:flags=lanczos', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '36', '-g', '8', '-keyint_min', '8', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', f'{OUT}/film-hd.webm')
    sh('ffmpeg', '-y', '-ss', '0.8', '-i', f'{tmp}/j.mp4', '-frames:v', '1', '-vf', 'scale=1920:-2', '-c:v', 'libwebp', '-quality', '80', f'{OUT}/film-poster.webp')
    print('film total', sum(d for _, _, d in FILM), 's', 'hd', mb(f'{OUT}/film-hd.mp4'), 'sd', mb(f'{OUT}/film-sd.mp4'), 'webm', mb(f'{OUT}/film-hd.webm'), 'MB')
