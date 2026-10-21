"""out/contact-sheet.png: 4 key frames per variant (from work/qc, i.e. the encoded MP4s)."""
import json
from PIL import Image, ImageDraw, ImageFont
meta = json.load(open('work/variants-meta.json'))['VARIANTS']
FW, FH, LAB, GAP = 480, 120, 190, 8
W = LAB + 4 * (FW + GAP)
H = 60 + len(meta) * (FH + GAP + 18)
sheet = Image.new('RGB', (W, H), (18, 22, 20))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except OSError:
    font = small = ImageFont.load_default()
d.text((12, 18), 'Animated B2B banners 1584x396 - key frames (frame number / seconds)', fill=(230, 240, 235), font=font)
for r, v in enumerate(meta):
    y = 60 + r * (FH + GAP + 18)
    d.text((12, y + 30), v['id'].upper(), fill=(82, 255, 186), font=font)
    d.text((12, y + 56), v['slug'], fill=(200, 210, 205), font=small)
    d.text((12, y + 76), f"{v['frames'] / 30:.0f} s", fill=(150, 160, 155), font=small)
    for c, fr in enumerate(v['contact']):
        im = Image.open(f"work/qc/{v['id']}/f{fr:03d}.png").convert('RGB').resize((FW, FH), Image.LANCZOS)
        x = LAB + c * (FW + GAP)
        sheet.paste(im, (x, y))
        d.text((x, y + FH + 2), f'f{fr}  {fr / 30:.1f}s', fill=(150, 160, 155), font=small)
sheet.save('out/contact-sheet.png')
print(sheet.size)
