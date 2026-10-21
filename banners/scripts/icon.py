"""Crop the ChatGPT icon (as used in the source banner) with an antialiased circular mask."""
import numpy as np
from PIL import Image
A = Image.open('source/banner-2.png').convert('RGB')
cx, cy, r = 1132.5, 95.0, 17.4
S = 40
crop = A.crop((int(cx - S/2), int(cy - S/2), int(cx - S/2) + S, int(cy - S/2) + S))
ox, oy = int(cx - S/2), int(cy - S/2)
ss = 8
yy, xx = np.mgrid[0:S*ss, 0:S*ss]
d = np.hypot((xx + .5)/ss + ox - cx, (yy + .5)/ss + oy - cy)
m = (d <= r).reshape(S, ss, S, ss).mean((1, 3))
rgba = np.dstack([np.asarray(crop), (m*255).astype(np.uint8)])
Image.fromarray(rgba, 'RGBA').save('public/chatgpt-icon.png')
