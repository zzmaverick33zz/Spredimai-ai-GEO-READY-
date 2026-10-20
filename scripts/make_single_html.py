#!/usr/bin/env python3
"""Builds out/bigfoot-floors-draft.html: one self-contained file (CSS, JS and media inlined). Run after `npm run build`."""
import base64, json, os, re, mimetypes
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(R, 'dist'); os.makedirs(os.path.join(R, 'out'), exist_ok=True)
def uri(path):
    p = os.path.join(D, path.lstrip('/'))
    mt = mimetypes.guess_type(p)[0] or {'.avif': 'image/avif', '.webm': 'video/webm'}.get(os.path.splitext(p)[1], 'application/octet-stream')
    if p.endswith('.avif'): mt = 'image/avif'
    return 'data:%s;base64,%s' % (mt, base64.b64encode(open(p, 'rb').read()).decode())
def pick(srcset, want):  # srcset 'a 640w, b 960w' -> path of width closest to want
    items = [(int(x.split()[1][:-1]), x.split()[0]) for x in srcset.split(', ')]
    return min(items, key=lambda t: abs(t[0] - want))[1]
h = open(os.path.join(D, 'index.html'), encoding='utf8').read()
M = json.load(open(os.path.join(D, 'media', 'manifest.json')))
out = {}
for k, m in M.items():
    if k.startswith('_'): continue
    if m['type'] == 'image':
        webp = pick(m['sources'][1]['srcset'], 900)
        jpg = pick(m['sources'][2]['srcset'], 1024)
        out[k] = {**{x: m[x] for x in ('type', 'alt', 'width', 'height')}, 'src': uri(webp), 'sources': []}
    else:
        srcs = [{'src': uri(s['src']), 'type': s['type'], **({'media': s['media']} if 'media' in s else {})} for s in m['sources'] if s['type'] == 'video/mp4']
        out[k] = {'type': 'video', 'poster': uri(m['poster'].replace('.avif', '.jpg')), 'sources': srcs, 'alt': m.get('alt', '')}
        if m.get('posterMobile'): out[k]['posterMobile'] = uri(m['posterMobile'].replace('.avif', '.jpg'))
# hero picture: swap srcsets for one webp each
def hero(mt):
    return uri(pick(mt, 1000))
h = re.sub(r'<link rel="preload"[^>]*>\n?', '', h)
def pic(m):
    block = m.group(0)
    block = re.sub(r'<source media="\(max-width:759px\)" srcset="([^"]*\.avif[^"]*)"[^>]*>', lambda x: '<source media="(max-width:759px)" srcset="%s" type="image/webp">' % uri(pick(x.group(1).replace('.avif', '.webp'), 844)), block, 1)
    block = re.sub(r'<source srcset="([^"]*\.avif[^"]*)"[^>]*>', lambda x: '<source srcset="%s" type="image/webp">' % uri(pick(x.group(1).replace('.avif', '.webp'), 1600)), block, 1)
    block = re.sub(r'<source[^>]*type="image/webp"(?![^>]*data:)[^>]*>\n?\s*', '', block)
    block = re.sub(r'src="(/media/[^"]+\.jpg)"', lambda x: 'src="%s"' % uri(x.group(1)), block)
    return block
h = re.sub(r'<picture>.*?</picture>', pic, h, count=1, flags=re.S)
css = ''.join(open(os.path.join(D, x.lstrip('/')), encoding='utf8').read() for x in re.findall(r'<link rel="stylesheet" crossorigin href="(/assets/[^"]+\.css)">', h))
h = re.sub(r'<link rel="stylesheet" crossorigin href="/assets/[^"]+\.css">', '', h)
h = h.replace('</head>', '<style>' + css + '</style></head>')
js = open(os.path.join(D, re.search(r'src="(/assets/[^"]+\.js)"', h).group(1).lstrip('/')), encoding='utf8').read()
h = re.sub(r'<script type="module" crossorigin src="/assets/[^"]+\.js"></script>', '', h)
inline = '<script>window.__MANIFEST__=' + json.dumps(out).replace('</', '<\\/') + '</script>'
h = h.replace('</body>', inline + '<script type="module">' + js.replace('</script', '<\\/script') + '</script></body>')
open(os.path.join(R, 'out', 'bigfoot-floors-draft.html'), 'w', encoding='utf8').write(h)
print(round(len(h) / 1e6, 2), 'MB')
