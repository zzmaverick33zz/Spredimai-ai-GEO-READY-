"""work/qc/vNN/*.png -> work/qc/vNN.png (2 columns, half size, frame labels)."""
import sys, glob, os
from PIL import Image, ImageDraw
for vid in sys.argv[1:]:
    files = sorted(glob.glob(f'work/qc/{vid}/f*.png'))
    W, H = 792, 198
    cols = 2
    rows = (len(files) + 1) // 2
    sheet = Image.new('RGB', (W * cols + 10, rows * (H + 6)), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, fn in enumerate(files):
        im = Image.open(fn).convert('RGB').resize((W, H), Image.LANCZOS)
        x, y = (i % cols) * (W + 10), (i // cols) * (H + 6)
        sheet.paste(im, (x, y))
        lab = os.path.basename(fn)[1:4]
        d.rectangle((x, y, x + 46, y + 18), fill=(0, 0, 0))
        d.text((x + 4, y + 3), f'f{lab}', fill=(255, 255, 0))
    sheet.save(f'work/qc/{vid}.png')
