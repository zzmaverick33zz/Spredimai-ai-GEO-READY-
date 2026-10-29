#!/usr/bin/env python3
"""One self-contained HTML per quality level (css, js and media inlined as data URIs).
  python3 build_single.py hd a|b|c     -> dist/Big_Foot_Floors_Studio_HD.html     full quality (hd video tier, ~45 MB): the file to download and open
  python3 build_single.py light  -> dist/Big_Foot_Floors_light.html  small (<16 MB) for the web preview / artifact
  python3 build_single.py hd-webm  (test only) same as hd but with the webm tier, for browsers without H.264 (headless Chromium)
The folder build (serve with serve.py) is still the reference; the scenes play at natural speed, so nothing here needs video seeking."""
import re, base64, os, subprocess, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
mode = sys.argv[1] if len(sys.argv) > 1 else 'hd'
page = sys.argv[2] if len(sys.argv) > 2 else 'a'      # a, b or c
mt = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.mp4': 'video/mp4', '.webm': 'video/webm'}
uri = lambda p: 'data:%s;base64,%s' % (mt[os.path.splitext(p)[1]], base64.b64encode(open(p, 'rb').read()).decode())
os.makedirs('dist/xs', exist_ok=True)
def xs(p):                                     # light tier: 640 px wide, made on demand from the sd file
    q = p.replace('-sd.mp4', '-xs.mp4')
    if os.path.exists(q): return q
    q = 'dist/xs/' + os.path.basename(q)
    if not os.path.exists(q):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-an', '-vf', 'scale=640:-2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '33', '-movflags', '+faststart', q], check=True)
    return q
def fix_video(m):
    v = m.group(0)
    srcs = re.findall(r'<source src="(media/[^"]+)"[^>]*>', v)
    keep = None
    base = {re.sub(r'-(hd|sd|xs)\.(mp4|webm)$', '', s) for s in srcs}
    tier = {'hd': 'hd.mp4', 'hd-webm': 'hd.webm', 'light': 'sd.mp4'}[mode]
    pick = [s for s in srcs if s.endswith('-' + tier)] or [s for s in srcs if s.endswith('-sd.mp4')] or srcs[:1]
    src = pick[0]
    v = re.sub(r'<source [^>]*>', '', v)
    return v.replace('</video>', '<source src="%s" type="%s"></video>' % (src, 'video/webm' if src.endswith('.webm') else 'video/mp4'))
h = open(page + '.html', encoding='utf8').read()
h = re.sub(r'<link rel="preload"[^>]*>\n?', '', h)
h = re.sub(r'<video[^>]*>.*?</video>', fix_video, h, flags=re.S)
h = re.sub(r'<link rel="stylesheet" href="(css/[^"]+)">', lambda m: '<style>' + open(m.group(1), encoding='utf8').read() + '</style>', h)
h = re.sub(r'<script src="([^"]+)"></script>', lambda m: '<script>' + open(m.group(1), encoding='utf8').read().replace('</script', '<\\/script') + '</script>', h)
def media(m):
    p = m.group(0)
    if not os.path.exists(p): return p
    if mode == 'light' and p.endswith('-sd.mp4'): p = xs(p)
    return uri(p)
h = re.sub(r'media/[A-Za-z0-9_.\-]+\.(?:webp|jpg|mp4|webm)', media, h)
out = {'hd': f'Big_Foot_Floors_Designer_{page.upper()}_HD.html', 'light': f'Big_Foot_Floors_Designer_{page.upper()}_light.html', 'hd-webm': 'test-hd-webm.html'}[mode]
open('dist/' + out, 'w', encoding='utf8').write(h)
print(out, round(len(h) / 1e6, 2), 'MB')
