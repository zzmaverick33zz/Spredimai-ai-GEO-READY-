#!/usr/bin/env python3
"""Inlines css, js, vendor and media into one self-contained HTML: dist/Big_Foot_Floors_premium.html"""
import re, base64, os, mimetypes
os.chdir(os.path.dirname(os.path.abspath(__file__)))
mt = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.mp4': 'video/mp4', '.avif': 'image/avif', '.png': 'image/png'}
def lite(p):
    b, e = os.path.splitext(p); q = b + '-lite' + e
    return q if e == '.mp4' and os.path.exists(q) else p
def uri(p): return 'data:%s;base64,%s' % (mt[os.path.splitext(p)[1]], base64.b64encode(open(p, 'rb').read()).decode())
h = open('index.html', encoding='utf8').read()
h = re.sub(r'<link rel="preload"[^>]*>\n?', '', h)
h = re.sub(r'<link rel="stylesheet" href="(css/[^"]+)">', lambda m: '<style>' + open(m.group(1), encoding='utf8').read() + '</style>', h)
h = re.sub(r'<script src="([^"]+)"></script>', lambda m: '<script>' + open(m.group(1), encoding='utf8').read().replace('</script', '<\\/script') + '</script>', h)
h = re.sub(r'<source src="media/[^"]+\.webm"[^>]*>', '', h)   # single file: mp4 only (lite)
h = re.sub(r'media/[A-Za-z0-9_.\-]+\.(?:webp|jpg|mp4|avif|png)', lambda m: uri(lite(m.group(0))) if os.path.exists(m.group(0)) else m.group(0), h)
h = h.replace(' loading="lazy"', '')   # data URIs: nothing to defer
os.makedirs('dist', exist_ok=True); open('dist/Big_Foot_Floors_premium.html', 'w', encoding='utf8').write(h)
print(round(len(h) / 1e6, 2), 'MB', 'leftover refs:', len(re.findall(r'(?:src|href|poster)="(?:media|css|js|vendor)/', h)))
