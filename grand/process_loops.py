#!/usr/bin/env python3
"""Seamless loops for every in-page video (hero, chapters, interiors). Same recipe as process_scenes.py:
 1. find cuts inside the planned range (ffmpeg scene detection) and keep the longest cut-free piece
 2. crop to the slot's aspect, then make the loop: cross-fade loop ('xf') for action, boomerang ('pp') for textures / camera moves,
    slow motion (x2) first when the piece is shorter than ~2.4 s
 3. encode hd / sd / webm + poster
Run: python3 grand/process_loops.py [names]   (needs source-media/ultra)"""
import os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = f'{R}/source-media/ultra'; OUT = f'{R}/grand/media'
TMP = '/tmp/claude-0/loops'; os.makedirs(TMP, exist_ok=True)
ASP = {'16:9': (16, 9), '4:5': (4, 5), '1:1': (1, 1), '21:9': (21, 9), '9:16': (9, 16), '16:10': (16, 10)}
WD = {'16:9': (1920, 1280), '4:5': (1080, 720), '1:1': (1080, 720), '21:9': (1920, 1280), '9:16': (1080, 640), '16:10': (1600, 1024)}
# name, file, start, planned length, aspect, focus-x, loop mode when the piece is short
CLIPS = [  # name, file, start, length of ONE cut-free piece, aspect, focus-x, loop mode
 ('s01-hero',      'Discovery.mp4', 48.58, 2.3, '16:9', .5, 'pp'),
 ('s03-dive',      'Discovery.mp4', 38.58, 2.3, '4:5', .55, 'xf'),
 ('s04-detail',    'Discovery.mp4', 71.12, 1.2, '1:1', .5, 'pp'),
 ('s05-lift',      'Discovery.mp4', 60.88, 1.05, '16:9', .5, 'pp'),
 ('s05-lift-9x16', 'Discovery.mp4', 60.88, 1.05, '9:16', .5, 'pp'),
 ('s11-grain',     'Discovery.mp4', 72.5, 0.95, '1:1', .5, 'pp'),
 ('s10-hands',     'WIDE BOARD.mp4', 19.8, 0.85, '4:5', .7, 'pp'),
 ('s12-fitted',    'WIDE BOARD.mp4', 40.8, 0.85, '16:10', .5, 'pp'),
 ('s13-home',      'ANTAKALNIS_INTERJERAS.mp4', 6.25, 0.87, '21:9', .5, 'pp'),
]
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def crop(asp, fx):
    a, b = ASP[asp]; return f"crop='if(gt(iw/ih,{a}/{b}),ih*{a}/{b},iw)':'if(gt(iw/ih,{a}/{b}),ih,iw*{b}/{a})':'(iw-ow)*{fx}':'(ih-oh)*0.5'"
def cuts(f, t0, d):
    p = subprocess.run(['ffmpeg', '-ss', str(t0), '-t', str(d), '-i', f'{SRC}/{f}', '-vf', "scale=320:-2,select='gt(scene,0.18)',showinfo", '-an', '-f', 'null', '-'], capture_output=True, text=True)
    return [float(x) for x in re.findall(r'pts_time:([0-9.]+)', p.stderr)]
only = set(sys.argv[1:]); GRADE = 'eq=contrast=1.04'
for name, f, t0, d, asp, fx, short in CLIPS:
    if only and name not in only: continue
    L = d; s0 = t0
    mode = short; slow = 1 if L >= 2.5 else (2 if L >= 1.15 else 3)
    F = min(1.0, round(L * slow * 0.25, 2)) if mode == 'xf' else 0
    base = f'{TMP}/{name}-base.mp4'
    vf = f"{crop(asp, fx)},scale={WD[asp][0]}:-2:flags=lanczos,{GRADE},fps=25"
    if slow > 1: vf += f',setpts={slow}*PTS,minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:vsbmc=1'
    sh('ffmpeg', '-y', '-ss', str(s0), '-t', str(L), '-i', f'{SRC}/{f}', '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', base)
    D = dur(base); loop = f'{TMP}/{name}-loop.mp4'
    if mode == 'pp': fc = '[0:v]split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1:a=0[o]'
    else: fc = (f'[0:v]split=3[a][b][c];[a]trim=start={F}:end={D - F},setpts=PTS-STARTPTS[mid];[b]trim=start={D - F}:end={D},setpts=PTS-STARTPTS[tail];'
                f'[c]trim=start=0:end={F},setpts=PTS-STARTPTS[head];[tail][head]xfade=transition=fade:duration={F}:offset=0[x];[x][mid]concat=n=2:v=1:a=0[o]')
    sh('ffmpeg', '-y', '-i', base, '-filter_complex', fc, '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'fast', '-pix_fmt', 'yuv420p', loop)
    LL = dur(loop); sizes = []
    for tag, w, crf in (('hd', WD[asp][0], 26), ('sd', WD[asp][1], 28)):
        sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', f'scale={w}:-2:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', f'{OUT}/{name}-{tag}.mp4'); sizes.append(round(os.path.getsize(f'{OUT}/{name}-{tag}.mp4') / 1e6, 2))
    sh('ffmpeg', '-y', '-i', loop, '-an', '-vf', f'scale={WD[asp][0]}:-2:flags=lanczos', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '36', '-row-mt', '1', f'{OUT}/{name}-hd.webm'); sizes.append(round(os.path.getsize(f'{OUT}/{name}-hd.webm') / 1e6, 2))
    xs = f'{OUT}/{name}-xs.mp4'
    if os.path.exists(xs): os.remove(xs)
    sh('ffmpeg', '-y', '-ss', str(LL * .5), '-i', loop, '-frames:v', '1', '-vf', f'scale={WD[asp][0]}:-2:flags=lanczos', '-c:v', 'libwebp', '-quality', '82', f'{OUT}/{name}-poster.webp')
    print(name, f'piece {L:.1f}s mode {mode}{"/slow" if slow > 1 else ""} -> loop {LL:.1f}s', sizes, 'MB', flush=True)
