import numpy as np
from PIL import Image
m = Image.open('public/mascot.png'); s = Image.open('public/mascot-shadow.png')
W,H = m.size
tiles=[]
for col in [(255,255,255),(10,20,16),(82,255,186),(20,60,48)]:
    bg = Image.new('RGBA',(W,H),col+(255,))
    bg.alpha_composite(s); bg.alpha_composite(m); tiles.append(bg)
sheet = Image.new('RGBA',(W*4,H)); [sheet.paste(t,(i*W,0)) for i,t in enumerate(tiles)]
sheet.save('work/cut_sheet.png')
# zoom edges on dark bg
z = tiles[1].crop((0,H//2-80,160,H//2+80)).resize((480,480),Image.NEAREST)
z2 = tiles[0].crop((W-160,60,W,220)).resize((480,480),Image.NEAREST)
z3 = tiles[1].crop((W//2-80,H-120,W//2+80,H)).resize((480,360),Image.NEAREST)
zz=Image.new('RGBA',(1440,480)); zz.paste(z,(0,0)); zz.paste(z2,(480,0)); zz.paste(z3,(960,0)); zz.save('work/cut_zoom.png')
# reconstruction error vs source on original gradient
src = np.asarray(Image.open('source/banner-2.png').convert('RGB')).astype(float)
t = np.arange(1584)/1583
g = (np.array([82,255,186.])*(1-t[:,None]) + np.array([49,84,71.])*t[:,None])[None].repeat(396,0)
canvas = Image.fromarray(g.astype(np.uint8)).convert('RGBA')
canvas.alpha_composite(s,(750,21)); canvas.alpha_composite(m,(750,21))
rec = np.asarray(canvas.convert('RGB')).astype(float)
d = np.abs(rec-src)[21:364,750:1083].max(2)
print('reconstruction err mean %.2f p99 %.1f max %.0f' % (d.mean(), np.percentile(d,99), d.max()))
