#!/usr/bin/env python3
"""Builds public/media/* and manifest.json from source-media/ (see MEDIA_MAP.md for why each file was chosen).
Run: python3 scripts/process_media.py"""
import json, os, subprocess, tempfile, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source-media')
OUT = os.path.join(ROOT, 'public', 'media')
Z1 = os.path.join(SRC, 'zip-drive-download-1', 'WhatsApp Image 2026-10-09 at %s.jpeg')
VID = os.path.join(SRC, 'videos', 'WhatsApp_Video_2026-10-09_at_%s.mp4')
CHAT = os.path.join(SRC, 'chat-photos', '%s.jpg')
SITE_DIR = os.path.join(SRC, 'site')
SITE = sorted(f for f in os.listdir(SITE_DIR) if not f.endswith('logo-2.png')) if os.path.isdir(SITE_DIR) else []
def site(i): return os.path.join(SITE_DIR, SITE[i])
os.makedirs(OUT, exist_ok=True)

# colour grades per chapter family (applied before encoding)
COLD = "colorbalance=rs=-0.06:gs=0.02:bs=0.08:rm=-0.04:bm=0.05,eq=saturation=0.8:gamma=0.95:brightness=-0.03"
NEUTRAL = "eq=saturation=0.9:contrast=1.03"
DEEP = "colorbalance=rs=-0.05:gs=0.02:bs=0.06,eq=saturation=0.55:gamma=1.05:brightness=-0.05:contrast=1.05"
NONE = "eq=saturation=1.0"
WARM = "colorbalance=rs=0.04:bs=-0.04:rm=0.03:bm=-0.03,eq=saturation=0.95:gamma=0.97"

def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def crop_box(w, h, aspect, fx=.5, fy=.5):
    ar = aspect[0] / aspect[1]
    if w / h > ar: cw, ch = round(h * ar), h
    else: cw, ch = w, round(w / ar)
    x = min(max(round(w * fx - cw / 2), 0), w - cw); y = min(max(round(h * fy - ch / 2), 0), h - ch)
    return cw, ch, x, y

def photo(slot, name, src, aspect, widths, grade, alt, fx=.5, fy=.5, sizes='100vw'):
    w, h = Image.open(src).size
    cw, ch, x, y = crop_box(w, h, aspect, fx, fy)
    tmp = os.path.join(tempfile.mkdtemp(), 'g.png')
    run('ffmpeg', '-y', '-i', src, '-vf', f'crop={cw}:{ch}:{x}:{y},{grade}', tmp)
    base = Image.open(tmp).convert('RGB')
    ws = sorted({min(v, cw) for v in widths})
    sets = {'avif': [], 'webp': [], 'jpg': []}
    for tw in ws:
        th = round(tw * ch / cw)
        im = base.resize((tw, th), Image.LANCZOS)
        im.save(f'{OUT}/{name}-{tw}.avif', quality=52, speed=6)
        im.save(f'{OUT}/{name}-{tw}.webp', quality=74, method=6)
        im.save(f'{OUT}/{name}-{tw}.jpg', quality=78, optimize=True, progressive=True)
        for k in sets: sets[k].append(f'/media/{name}-{tw}.{k} {tw}w')
    tw = ws[-1]; th = round(tw * ch / cw)
    return {'type': 'image', 'alt': alt, 'width': tw, 'height': th, 'src': f'/media/{name}-{tw}.jpg',
            'sources': [{'srcset': ', '.join(sets['avif']), 'type': 'image/avif', 'sizes': sizes},
                        {'srcset': ', '.join(sets['webp']), 'type': 'image/webp', 'sizes': sizes},
                        {'srcset': ', '.join(sets['jpg']), 'type': 'image/jpeg', 'sizes': sizes}]}

def video(name, src, t0, t1, aspect, grade, fx=.5, stab=True, scale_w=None):
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src]).decode().strip().split(',')
    w, h = int(probe[0]), int(probe[1])
    rot = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream_side_data=rotation', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip()
    if rot in ('-90', '90'): w, h = h, w
    cw, ch, x, y = crop_box(w, h, aspect, fx, .5)
    cw -= cw % 2; ch -= ch % 2
    trf = os.path.join(tempfile.mkdtemp(), 't.trf')
    base = f'trim=start={t0}:end={t1},setpts=PTS-STARTPTS'
    pre = f'{base},crop={cw}:{ch}:{x}:{y}'
    if stab:
        run('ffmpeg', '-y', '-i', src, '-vf', f'{pre},vidstabdetect=shakiness=6:accuracy=9:result={trf}', '-f', 'null', '-')
        vf = f'{pre},vidstabtransform=input={trf}:smoothing=20:zoom=4:optzoom=0,hqdn3d=4:3:8:6,{grade},fps=24,format=yuv420p'
    else:
        vf = f'{pre},hqdn3d=4:3:8:6,{grade},fps=24,format=yuv420p'
    run('ffmpeg', '-y', '-i', src, '-an', '-vf', vf, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '44', '-row-mt', '1', f'{OUT}/{name}.webm')
    run('ffmpeg', '-y', '-i', src, '-an', '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '32', '-movflags', '+faststart', f'{OUT}/{name}.mp4')
    run('ffmpeg', '-y', '-i', f'{OUT}/{name}.mp4', '-frames:v', '1', f'{OUT}/{name}-poster.png')
    p = Image.open(f'{OUT}/{name}-poster.png').convert('RGB'); os.remove(f'{OUT}/{name}-poster.png')
    p.save(f'{OUT}/{name}-poster.avif', quality=50, speed=6); p.save(f'{OUT}/{name}-poster.jpg', quality=76)
    return {'webm': f'/media/{name}.webm', 'mp4': f'/media/{name}.mp4', 'poster': f'/media/{name}-poster.avif', 'w': cw, 'h': ch}

def vsrc(v, media=None):
    out = []
    for k, t in (('webm', 'video/webm'), ('mp4', 'video/mp4')):
        s = {'src': v[k], 'type': t}
        if media: s['media'] = media
        out.append(s)
    return out

M = {}
SZ_MAIN = '(min-width:900px) 58vw, 100vw'

# S01 hero: night crane lifting a root mass (photo, slow zoom in JS). Desktop 16:9, mobile portrait.
M['S01'] = photo('S01', 's01-hero', Z1 % '20.00.28', (16, 9), [1000, 1600, 2000], COLD, 'At night a truck-mounted crane lifts a huge root mass of an ancient trunk over a loaded trailer', fx=.6, fy=.4)
M['S01']['mobile'] = photo('S01', 's01-hero-m', Z1 % '20.00.28', (9, 16), [480, 844], COLD, M['S01']['alt'], fx=.5, fy=.5, sizes='100vw')

# S02: uprooted trunk with its root ball on a trailer
M['S02'] = photo('S02', 's02-fallen', Z1 % '20.16.41 (1)', (4, 5), [640, 960], DEEP, 'A huge uprooted bog oak with its root ball, resting on a trailer in the yard', fx=.6, sizes=SZ_MAIN)

# S03: the team at the river with a trunk (photo from bffloors.com, bog-wood page)
M['S03'] = photo('S03', 's03-dive', site(60), (4, 5), [640, 960, 1280], COLD, 'A diver stands in a misty river beside a huge black bog trunk lying on the bank', fx=.38, sizes=SZ_MAIN)

# S04: detail, a short loop of the trunk's bark at the lake shore (video, 1:1)
v = video('s04-detail', VID % '20.05.10', 5.0, 13.0, (1, 1), COLD, fx=.55)
M['S04'] = {'type': 'video', 'poster': v['poster'], 'sources': vsrc(v), 'alt': 'Bark of a bog trunk lying on the lake shore'}

# S05: lift. Desktop 16:9 (excavator draws the trunk out), mobile 9:16 (trunk hauled out of the lake)
vd = video('s05-lift', VID % '20.05.08', 12.0, 18.5, (16, 9), COLD)
vm = video('s05-lift-9x16', VID % '20.05.23', 52.0, 62.0, (9, 16), COLD)
M['S05'] = {'type': 'video', 'poster': vd['poster'], 'posterMobile': vm['poster'], 'sources': vsrc(vm, '(max-width: 899px)') + vsrc(vd),
            'alt': 'A trunk is drawn out of the sand and water at the lake shore'}

# S06: carbon-dating disc with measuring tape
M['S06'] = photo('S06', 's06-dated', CHAT % '11', (16, 10), [640, 1024, 1600], NEUTRAL, 'Cross-section disc of a bog trunk by the lake, measured with a tape', sizes=SZ_MAIN)

# S07: first cut, slab on the saw
M['S07'] = photo('S07', 's07-first-cut', CHAT % '13', (4, 5), [640, 1024, 1200], WARM, 'A freshly sawn bog oak slab on the saw bed: black bark and a golden-brown heart', fy=.45, sizes=SZ_MAIN)

# S08: cross-section rings
M['S08'] = photo('S08', 's08-rings', Z1 % '20.16.20', (1, 1), [640, 1024, 1500], WARM, 'Freshly cut cross-section of a bog log with pale heartwood rings', fy=.42, sizes='(min-width:900px) 32vw, 56vw')



# ---- photos from the client's current site (bffloors.com), placed where the site itself uses them ----
SZ_COL = '(min-width:900px) 25vw, 50vw'
SZ_PRODUCT = '(min-width:1080px) 25vw, (min-width:760px) 50vw, 100vw'
S = lambda slot, name, i, aspect, widths, alt, **kw: M.__setitem__(slot, photo(slot, name, site(i), aspect, widths, kw.pop('grade', NONE), alt, **kw))
S('S09', 's09-stacks', 62, (16, 10), [640, 1024, 1600], 'Boards stacked on racks with gaps between the layers', grade=WARM, sizes=SZ_MAIN)
S('S10', 's10-hands', 56, (4, 5), [640, 1024, 1200], 'A craftsman in the workshop assembling a star-shaped parquet medallion', grade=WARM, fx=.55, sizes=SZ_MAIN)
S('S11', 's11-inlay', 45, (1, 1), [640, 1024, 1500], 'A dark bog-oak footprint inlaid into pale oak, the Big Foot mark', grade=WARM, sizes='(min-width:900px) 32vw, 56vw')
S('S12', 's12-fitted', 70, (16, 10), [640, 1024, 1600, 2000], 'A finished vaulted corridor with a laid parquet floor', grade=WARM, fy=.6, sizes=SZ_MAIN)
S('S13', 's13-home', 53, (21, 9), [640, 1024, 1600, 2400], 'A living room with floor-to-ceiling windows, mountains outside, and a warm oak floor', fy=.62, sizes='100vw')
S('S14', 's14-bog-oak', 61, (3, 4), [480, 800, 1006], 'Bog oak chevron boards', sizes=SZ_COL)
S('S15', 's15-bog-ash', 64, (3, 4), [480, 800, 1200], 'Bog ash in a hexagon pattern', sizes=SZ_COL)
S('S16', 's16-oak', 9, (3, 4), [480, 800, 1200], 'Oak floor laid in a sunburst pattern', sizes=SZ_COL)
S('S17', 's17-elm', 69, (3, 4), [480, 800, 1200], 'Elm slab with golden grain', sizes=SZ_COL)
S('S18', 's18-ash', 27, (3, 4), [480, 800, 1200], 'Ash planks with pale, flowing grain', sizes=SZ_COL)
S('S19', 's19-black-walnut', 19, (3, 4), [480, 800, 1200], 'Black walnut parquet in a broken geometric pattern', sizes=SZ_COL)
S('S20', 's20-floors', 5, (4, 5), [640, 1024, 1500], 'A marquetry floor with a star medallion in a long corridor', sizes='(min-width:1080px) 50vw, 100vw')
S('S21', 's21-stairs', 21, (4, 5), [640, 1024, 1500], 'A spiral staircase in pale wood seen from above', sizes=SZ_PRODUCT)
S('S22', 's22-walls', 24, (4, 5), [640, 1024, 1500], 'A bedroom with wood-panelled walls', sizes=SZ_PRODUCT)
S('S23', 's23-ceilings', 25, (4, 5), [640, 1024, 1500], 'A living room with a wood ceiling', sizes=SZ_PRODUCT)
S('S24', 's24-tables', 7, (4, 5), [640, 1024, 1500], 'A dark wooden table with a live edge in a dark room', sizes=SZ_PRODUCT)
S('S25', 's25-wine-cellar', 50, (16, 9), [640, 1024, 1600, 1920], 'A wine cellar with wooden racks and arched alcoves', sizes='(min-width:1080px) 50vw, 100vw')
S('S26', 's26-yachts', 0, (16, 9), [640, 1024, 1600, 1920], 'A yacht saloon with a round dining table on a pale wooden floor', sizes='(min-width:1080px) 50vw, 100vw')
S('S27', 's27-project-1', 54, (4, 5), [640, 1024, 1500], 'A staircase and timber walls in a private residence', fx=.5, sizes='(min-width:760px) 40vw, 82vw')
S('S28', 's28-project-2', 47, (4, 5), [640, 1024, 1500], 'A living room with oak walls and warm lighting', fx=.6, sizes='(min-width:760px) 40vw, 82vw')
S('S29', 's29-project-3', 1, (4, 5), [640, 1024, 1500], 'A lobby with a staircase and a pale wooden floor', fx=.55, sizes='(min-width:760px) 40vw, 82vw')
S('S30', 's30-project-4', 48, (4, 5), [640, 1024, 1500], 'A double-height living room with gold columns and a glass staircase', fx=.55, sizes='(min-width:760px) 40vw, 82vw')
S('S31', 's31-heritage', 66, (4, 5), [640, 1024, 1006], 'A woodworker standing beside a finished dark oak cabinet in the workshop', sizes='(min-width:900px) 40vw, 100vw')

M.pop('S01', None)  # S01 is written statically into index.html (LCP)
json.dump(M, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print('files', len(os.listdir(OUT)), 'total MB', round(tot / 1e6, 1))
for f in sorted(os.listdir(OUT)):
    if f.endswith(('.webm', '.mp4')): print(f, round(os.path.getsize(os.path.join(OUT, f)) / 1e6, 2), 'MB')
