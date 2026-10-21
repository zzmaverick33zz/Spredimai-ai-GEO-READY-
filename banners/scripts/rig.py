"""Split public/mascot.png into rig layers for character animation:
  public/rig/body.png   mascot with eyes + smile removed (holes filled by Laplace diffusion + matched noise)
  public/rig/eye-l.png, eye-r.png, mouth.png   the original pixels of each feature, feathered alpha
  public/rig/rig.json   feature boxes (in mascot.png coordinates)
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

src = np.asarray(Image.open('public/mascot.png').convert('RGBA')).astype(np.float64)
rgb, A = src[..., :3], src[..., 3]
L = rgb @ [0.299, 0.587, 0.114]
os.makedirs('public/rig', exist_ok=True)

FEATURES = {  # search boxes x0,y0,x1,y1, dark threshold, dilation
    'eye-l': ((108, 124, 184, 198), 95, 4),
    'eye-r': ((245, 124, 302, 198), 95, 4),
    'mouth': ((200, 168, 238, 194), 120, 3),
}
hole = np.zeros(L.shape, bool)
meta = {}
for name, ((x0, y0, x1, y1), thr, dil) in FEATURES.items():
    box = np.zeros(L.shape, bool); box[y0:y1, x0:x1] = True
    core = (L < thr) & box
    lab, n = ndimage.label(core)
    if n == 0:
        raise SystemExit(f'{name}: nothing found')
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    core = lab == (1 + int(np.argmax(sizes)))
    core = ndimage.binary_fill_holes(core)  # eye highlights live inside
    m = ndimage.binary_dilation(core, iterations=dil)
    hole |= m
    # feature layer: original pixels, soft alpha that fades over the dilated rim
    dist = ndimage.distance_transform_edt(~core)
    alpha = np.clip(1 - (dist - 1) / dil, 0, 1) * (A / 255)
    ys, xs = np.where(alpha > 0.01)
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    lay = np.dstack([rgb, alpha * 255])[by0:by1, bx0:bx1].astype(np.uint8)
    Image.fromarray(lay, 'RGBA').save(f'public/rig/{name}.png')
    cy, cx = ndimage.center_of_mass(core)
    meta[name] = dict(x=int(bx0), y=int(by0), w=int(bx1 - bx0), h=int(by1 - by0), cx=round(float(cx), 1), cy=round(float(cy), 1))

# Laplace (harmonic) fill of the holes, per channel, from the surrounding skin
# solve over the hole plus a band, so the darker socket shading around the eyes is smoothed too
solve = ndimage.binary_dilation(hole, iterations=5)
fill = rgb.copy()
ring = ndimage.binary_dilation(hole, iterations=8) & ~solve
for c in range(3):
    ch = fill[..., c]
    ch[solve] = ch[ring].mean()
    for _ in range(3000):
        avg = (np.roll(ch, 1, 0) + np.roll(ch, -1, 0) + np.roll(ch, 1, 1) + np.roll(ch, -1, 1)) / 4
        ch[solve] = avg[solve]
# match the fine texture: add noise with the std of the surrounding skin high-pass
hp = rgb - ndimage.gaussian_filter(rgb, (2, 2, 0))
sd = hp[ring].std(0) * 0.8
rng = np.random.default_rng(3)
# luminance-only grain (no chroma speckle)
noise = ndimage.gaussian_filter(rng.normal(0, 1, rgb.shape[:2]), 0.7)
noise /= noise.std()
fill[solve] += (noise[..., None] * sd.mean() * 0.45)[solve]
body = np.dstack([np.clip(fill, 0, 255), A]).astype(np.uint8)
Image.fromarray(body, 'RGBA').save('public/rig/body.png')
json.dump(meta, open('public/rig/rig.json', 'w'), indent=1)
print(json.dumps(meta))
