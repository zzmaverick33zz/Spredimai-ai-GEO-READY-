"""Cut the glass mascot out of banner-2.png.

The source background is an exact horizontal linear sRGB gradient
#52FFBA -> #315447, so the background plate is known per column. Pixels that
match bg*k (k<=1, same chroma) are the baked drop shadow; everything else is
the mascot. Outputs:
  public/mascot.png         mascot only, straight alpha, no shadow
  public/mascot-shadow.png  the baked contact shadow as a black alpha layer
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src = sys.argv[1]
outdir = sys.argv[2]
X0, X1, Y0, Y1 = 700, 1110, 0, 396

a = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
H, W, _ = a.shape
c0 = np.array([82, 255, 186.0]); c1 = np.array([49, 84, 71.0])
t = np.arange(W) / (W - 1)
bg = (c0[None, :] * (1 - t[:, None]) + c1[None, :] * t[:, None])[None, :, :].repeat(H, 0)

crop = a[Y0:Y1, X0:X1]; bgc = bg[Y0:Y1, X0:X1]
# best shadow factor k per pixel (least squares pixel ~ k*bg)
k = (crop * bgc).sum(2) / (bgc * bgc).sum(2)
k = np.clip(k, 0, 1.0)
resid = np.sqrt(((crop - k[..., None] * bgc) ** 2).sum(2))   # chroma deviation from bg
brighter = crop.sum(2) - bgc.sum(2)

obj = (resid > 14) | (brighter > 30)
obj = ndimage.binary_opening(obj, iterations=1)
lab, n = ndimage.label(obj)
sizes = ndimage.sum(obj, lab, range(1, n + 1))
keep = np.zeros_like(obj)
for i, s in enumerate(sizes, 1):
    if s > 3000:
        keep |= lab == i
keep = ndimage.binary_fill_holes(keep)
keep = ndimage.binary_closing(keep, iterations=3)
keep = ndimage.binary_fill_holes(keep)
print('components kept', sum(1 for s in sizes if s > 3000), 'px', keep.sum())

# soft edge: erode by 1px then blur -> antialiased alpha that sits inside the rim,
# so no bg-green fringe is carried out
core = ndimage.binary_erosion(keep, iterations=1)
alpha = ndimage.gaussian_filter(core.astype(float), 0.8)
alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)

# decontaminate edge pixels: where alpha<1, the pixel is a mix of fg and bg
# pixel = alpha*fg + (1-alpha)*bg  -> fg = (pixel - (1-alpha)*bg)/alpha
fg = crop.copy()
m = (alpha > 0.02) & (alpha < 0.999)
fg[m] = (crop[m] - (1 - alpha[m, None]) * bgc[m]) / alpha[m, None]
fg = np.clip(fg, 0, 255)

ys, xs = np.where(alpha > 0)
bx0, bx1, by0, by1 = xs.min() - 4, xs.max() + 5, ys.min() - 4, ys.max() + 5
rgba = np.dstack([fg, alpha * 255]).astype(np.uint8)[by0:by1, bx0:bx1]
Image.fromarray(rgba, 'RGBA').save(f'{outdir}/mascot.png')

# shadow layer: darkness outside the object
shadow = np.clip(1 - k, 0, 1)
shadow[keep] = 0
shadow = ndimage.gaussian_filter(shadow, 1.0)
shadow[shadow < 0.03] = 0
sh = np.zeros((*shadow.shape, 4), np.uint8)
sh[..., 3] = np.clip(shadow * 255, 0, 255)
Image.fromarray(sh[by0:by1 + 30, bx0 - 30:bx1 + 30] if False else sh[by0:by1, bx0:bx1], 'RGBA').save(f'{outdir}/mascot-shadow.png')
print('bbox in source', X0 + bx0, Y0 + by0, X0 + bx1, Y0 + by1, 'size', bx1 - bx0, by1 - by0)
