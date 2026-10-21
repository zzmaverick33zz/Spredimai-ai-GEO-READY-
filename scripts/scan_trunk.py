#!/usr/bin/env python3
"""'Scans' the reference trunk photo (source-media/generated/ai-9.jpg, an AI-generated image from the client) for the 3D trunk:
 - outline per slice along the axis (centre line + half height) and the ragged butt contour -> src/js/trunk-profile.json
 - the photo itself, levelled along the axis, with the sling painted out and the background bled out of the edges
   -> public/media/3d/trunk-photo.webp (projected onto the mesh by scene.js)
Needs numpy and Pillow only. Run: python3 scripts/scan_trunk.py"""
import json, os, collections
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = Image.open(f'{R}/source-media/generated/ai-9.jpg').convert('RGB'); W, H = img.size

# 1) paint the sling out: clone bark from 80 px back along the trunk, feathered
ang0 = 22.6; ca, sa = np.cos(np.radians(ang0)), np.sin(np.radians(ang0))
strap = [(596, 300), (640, 325), (668, 372), (690, 425), (705, 480), (706, 530), (690, 578), (655, 618), (612, 640), (590, 612), (630, 575), (660, 530), (664, 480), (650, 430), (626, 378), (588, 336)]
sm = Image.new('L', (W, H), 0); ImageDraw.Draw(sm).polygon(strap, fill=255)
sm = sm.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(5))
src = np.asarray(img).astype(float); yy, xx = np.mgrid[0:H, 0:W]
sx = np.clip((xx - 95 * ca).round().astype(int), 0, W - 1); sy = np.clip((yy - 95 * sa).round().astype(int), 0, H - 1)
clone = src[sy, sx]; al = (np.asarray(sm).astype(float) / 255)[..., None]
clean = Image.fromarray((src * (1 - al) + clone * al).astype('uint8'))

# 2) trunk mask (dark body against the pale sky), no crane, chains or drips
a = np.asarray(img).astype(float); lum = a.mean(2)
mask = (lum < 118) & (yy > 85) & (yy < 690) & (xx < 885)
mask &= ~((xx > 728) & (yy < 395 + (xx - 728) * 0.62))
topx = [205, 245, 280, 330, 400, 450, 520, 580, 625, 680, 740, 800, 860, 885]           # trunk's upper outline (hand-traced),
topy = [118, 150, 185, 213, 238, 258, 288, 318, 345, 392, 430, 466, 498, 512]           # keeps the dark sky between the chains out
mask &= ~((xx >= 205) & (yy < np.interp(xx, topx, topy) - 3))
m = Image.fromarray((mask * 255).astype('uint8')).filter(ImageFilter.MedianFilter(7)); m = np.asarray(m) > 127
seed = (int(H * .45), int(W * .45)); lab = np.zeros((H, W), bool); q = collections.deque([seed]); lab[seed] = True
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not lab[ny, nx]: lab[ny, nx] = True; q.append((ny, nx))
mk = Image.fromarray((lab * 255).astype('uint8'))
mk = mk.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MinFilter(31)).filter(ImageFilter.MaxFilter(31))
mk = np.asarray(mk) > 127; mk[:, 872:] = False
ys, xs = np.nonzero(mk); pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0)
_, _, vt = np.linalg.svd(pts - c, full_matrices=False); ax = vt[0]
if ax[0] < 0: ax = -ax
ang = float(np.degrees(np.arctan2(ax[1], ax[0])))

# 3) level everything along the axis (on a padded canvas so nothing rotates out of frame)
PADC = 320
def padimg(im, fill=0):
    out = Image.new(im.mode, (im.width + 2 * PADC, im.height + 2 * PADC), fill); out.paste(im, (PADC, PADC)); return out
ctr = (float(c[0]) + PADC, float(c[1]) + PADC)
rp = padimg(clean).rotate(ang, resample=Image.BICUBIC, center=ctr)
rm = np.asarray(padimg(Image.fromarray((mk * 255).astype('uint8'))).rotate(ang, resample=Image.NEAREST, center=ctr)) > 127
ys, xs = np.nonzero(rm); x0, x1 = int(xs.min()), int(xs.max()); y0, y1 = int(ys.min()), int(ys.max())
Lpx = x1 - x0; N = 64
# true bark edge per column: first / last row inside the mask whose (smoothed) luminance is bark-dark; the mask edge sits on the pale rim
lumR = np.asarray(rp.convert('L').filter(ImageFilter.GaussianBlur(2))).astype(float)
ytc = np.full(rm.shape[1], np.nan); ybc = np.full(rm.shape[1], np.nan)
for x in range(x0, x1 + 1):
    col_m = np.nonzero(rm[:, x])[0]
    if len(col_m) < 10: continue
    dark = col_m[lumR[col_m, x] < 80]
    if len(dark) > 10: ytc[x] = dark.min(); ybc[x] = dark.max()
xs_ok = np.nonzero(~np.isnan(ytc))[0]
ytc = np.interp(np.arange(len(ytc)), xs_ok, ytc[xs_ok]); ybc = np.interp(np.arange(len(ybc)), xs_ok, ybc[xs_ok])
edges = np.linspace(x0, x1, N + 1); yc = []; hh = []
for i in range(N):
    xa, xb = int(edges[i]), max(int(edges[i]) + 1, int(edges[i + 1]))
    lo = np.median(ytc[xa:xb]); hi = np.median(ybc[xa:xb]); yc.append((lo + hi) / 2); hh.append((hi - lo) / 2)
yc = np.array(yc); hh = np.array(hh); R0 = float(np.median(hh[N // 4:3 * N // 4]))
k = np.ones(3) / 3; hh = np.convolve(np.pad(hh, 1, mode='edge'), k, 'valid'); yc = np.convolve(np.pad(yc, 1, mode='edge'), k, 'valid')
cy_ref = float(yc[N // 4:3 * N // 4].mean())
# ragged butt: leftmost trunk pixel for every row of the bbox (fraction of length from the furthest tip)
rows = np.arange(y0, y1 + 1); left = np.full(len(rows), np.nan)
for j, r_ in enumerate(rows):
    xr = np.nonzero(rm[r_])[0]
    if len(xr): left[j] = xr.min()
ok = ~np.isnan(left); left = np.interp(np.arange(len(rows)), np.arange(len(rows))[ok], left[ok]); end = (left - x0) / Lpx

# 4) texture = levelled, cleaned photo cropped to the trunk bbox; bleed trunk colour outwards so edges never show sky
pad = 6; bx0, by0, bx1, by1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
print('bbox', bx0, by0, bx1, by1, 'rot size', rp.size)
ta = np.asarray(rp).astype(float)[by0:by1, bx0:bx1]; gx = np.arange(bx0, bx1).clip(0, len(ytc) - 1); inset = 3
rows_all = np.arange(by0, by1)[:, None]
between = (rows_all >= ytc[gx][None, :] + inset) & (rows_all <= ybc[gx][None, :] - inset)          # inside the bark edges
rm_c = rm[by0:by1, bx0:bx1]
butt = np.asarray(Image.fromarray((rm_c * 255).astype('uint8')).filter(ImageFilter.MinFilter(9))) > 127
butt &= (np.arange(bx0, bx1)[None, :] < x0 + 0.14 * Lpx)                                            # ragged end: trust the mask
tm = (between & rm_c) | butt
filled = tm.copy(); col = ta.copy()
for _ in range(40):
    if filled.all(): break
    acc = np.zeros_like(col); cnt = np.zeros(filled.shape)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        sh = np.roll(np.roll(col * filled[..., None], dy, 0), dx, 1); cs = np.roll(np.roll(filled, dy, 0), dx, 1)
        acc += sh; cnt += cs
    new = (~filled) & (cnt > 0); col[new] = acc[new] / cnt[new][:, None]; filled |= new
# soften the baked wet-sky glints (the 3D light provides its own sheen), keep the colour of the mud and bark
Lc = col.mean(2, keepdims=True); thr = 105.0
col = col * np.where(Lc > thr, (thr + 0.45 * (Lc - thr)) / np.maximum(Lc, 1), 1.0)
tex = Image.fromarray(np.clip(col, 0, 255).astype('uint8'))
os.makedirs(f'{R}/public/media/3d', exist_ok=True)
tw = 1280; th = int(tw * tex.height / tex.width); tex.resize((tw, th), Image.LANCZOS).save(f'{R}/public/media/3d/trunk-photo.webp', quality=88, method=6)
# cut-out: the levelled, cleaned photo with the trunk as alpha (shown as the very first frame, then handed over to the 3D mesh)
alpha = Image.fromarray((rm[by0:by1, bx0:bx1] * 255).astype('uint8')).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
rgba = rp.crop((bx0, by0, bx1, by1)).convert('RGBA'); rgba.putalpha(alpha)
cw = 1600; rgba.resize((cw, int(cw * rgba.height / rgba.width)), Image.LANCZOS).save(f'{R}/public/media/3d/trunk-cutout.webp', quality=90, method=6)
bw, bh = bx1 - bx0, by1 - by0
json.dump({
    'lenOverR': round(Lpx / R0, 3), 'angle': round(ang, 2),
    'bbox': [bw, bh], 'x0': x0 - bx0, 'len': Lpx,                       # px in the cropped texture
    'yc': [round(float(v - by0), 1) for v in yc], 'hh': [round(float(v), 1) for v in hh], 'R0': round(R0, 1), 'cy': round(cy_ref - by0, 1),
    'rowsTop': y0 - by0, 'end': [round(float(v), 4) for v in end]
}, open(f'{R}/src/js/trunk-profile.json', 'w'))
print('axis', round(ang, 1), 'L/R0', round(Lpx / R0, 2), 'tex', tex.size, '->', (tw, th))
tex.save('/tmp/claude-0/qa/trunk_tex_preview.png')
ov = np.asarray(rp).astype(float).copy(); ov[~rm] = ov[~rm] * 0.35
Image.fromarray(ov.astype('uint8')).crop((bx0, by0, bx1, by1)).save('/tmp/claude-0/qa/rot_mask_overlay.png')
