#!/usr/bin/env python3
"""One self-contained HTML (dist/Big_Foot_Floors_final.html): css, js and media inlined. Uses the -sd video tier only,
so the file stays small enough to open anywhere. Quality version = the folder (serve with serve.py)."""
import re, base64, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
mt = {'.webp': 'image/webp', '.jpg': 'image/jpeg', '.mp4': 'video/mp4'}
uri = lambda p: 'data:%s;base64,%s' % (mt[os.path.splitext(p)[1]], base64.b64encode(open(p, 'rb').read()).decode())
def xs(p):
    q = p.replace('-sd.mp4', '-xs.mp4'); return q if os.path.exists(q) else p
h = open('index.html', encoding='utf8').read()
h = re.sub(r'<link rel="preload"[^>]*>\n?', '', h)
h = re.sub(r'<source src="media/[^"]+-hd\.(?:mp4|webm)"[^>]*>', '', h)
h = h.replace(' media="(max-width: 899px)"', ' media="(max-width: 899px)"')
h = re.sub(r'<link rel="stylesheet" href="(css/[^"]+)">', lambda m: '<style>' + open(m.group(1), encoding='utf8').read() + '</style>', h)
h = re.sub(r'<script src="([^"]+)"></script>', lambda m: '<script>' + open(m.group(1), encoding='utf8').read().replace('</script', '<\\/script') + '</script>', h)
h = re.sub(r'media/[A-Za-z0-9_.\-]+\.(?:webp|jpg|mp4)', lambda m: uri(xs(m.group(0))) if os.path.exists(m.group(0)) else m.group(0), h)
os.makedirs('dist', exist_ok=True); open('dist/Big_Foot_Floors_final.html', 'w', encoding='utf8').write(h)
print(round(len(h) / 1e6, 2), 'MB')
