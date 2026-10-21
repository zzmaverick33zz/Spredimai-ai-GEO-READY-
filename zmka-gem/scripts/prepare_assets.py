#!/usr/bin/env python3
"""Build /public/brand and /public/work from source-assets/ (not in git).

source-assets/
  butterfly.jpg      pixel butterfly, magenta dither on white (logo_pfp-02)
  wordmark.png       ZM_KA GEM wordmark, black on transparent (logo-01)
  work/set-NN.jpg    portfolio photos, work/training.jpg

Usage: python3 scripts/prepare_assets.py   (needs Pillow; pillow-heif for .HEIC)
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-assets"
BRAND = ROOT / "public" / "brand"
WORK = ROOT / "public" / "work"
APP = ROOT / "app"

MAGENTA = (255, 0, 245)
LIGHT = (255, 214, 251)  # butterfly on dark blocks
INK = (18, 18, 18)


def butterfly_alpha(img: Image.Image) -> Image.Image:
    """Alpha mask from a magenta-on-white image.

    Magenta has G=0 and white has G=255, so 1 - G/255 is exactly how much
    magenta a pixel holds: no halo, no white fringe on the dither dots.
    """
    g = img.convert("RGB").getchannel("G")
    return g.point(lambda v: 0 if v > 240 else 255 - v)


def tint(alpha: Image.Image, rgb) -> Image.Image:
    out = Image.new("RGBA", alpha.size, rgb + (0,))
    out.putalpha(alpha)
    return out


def crop_to_content(img: Image.Image, pad: float = 0.04) -> Image.Image:
    box = img.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    l, t, r, b = box
    side = max(r - l, b - t)
    side = int(side * (1 + pad * 2))
    cx, cy = (l + r) // 2, (t + b) // 2
    return img.crop((cx - side // 2, cy - side // 2, cx - side // 2 + side, cy - side // 2 + side))


def sprite(alpha: Image.Image, size: int) -> Image.Image:
    """Hard-edged pixel sprite: box-downscale, then 1-bit alpha."""
    small = alpha.resize((size, size), Image.Resampling.BOX)
    return small.point(lambda v: 255 if v > 70 else 0)


def sprite_svg(mask: Image.Image, color: str) -> str:
    w, h = mask.size
    px = mask.load()
    d = []
    for y in range(h):
        x = 0
        while x < w:
            if px[x, y]:
                start = x
                while x < w and px[x, y]:
                    x += 1
                d.append(f"M{start} {y}h{x - start}v1h-{x - start}z")
            else:
                x += 1
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges"><path fill="{color}" d="{"".join(d)}"/></svg>\n'
    )


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    # Butterfly: transparent dither versions + pixel sprites.
    src = Image.open(SRC / "butterfly.jpg")
    full = crop_to_content(tint(butterfly_alpha(src), MAGENTA))
    alpha = full.getchannel("A")
    for name, rgb in (("butterfly", MAGENTA), ("butterfly-light", LIGHT)):
        img = tint(alpha, rgb)
        for px in (880, 600, 440):
            # Few alpha levels + lossless WebP: dither dots stay crisp and the
            # file is ~5x smaller than lossy (noise compresses badly when lossy).
            a_px = img.getchannel("A").resize((px, px), Image.Resampling.LANCZOS)
            a_px = a_px.point(lambda v: round(v / 255 * 5) * 51)
            tint(a_px, rgb).save(BRAND / f"{name}-{px}.webp", "WEBP", lossless=True, method=6)
    tint(alpha, MAGENTA).resize((880, 880), Image.Resampling.LANCZOS).save(BRAND / "butterfly.png", optimize=True)

    # 8-bit sprites, shown only at integer scale with image-rendering: pixelated.
    for px in (16, 32, 48):
        m = sprite(alpha, px)
        tint(m, MAGENTA).save(BRAND / f"butterfly-sprite-{px}.png", optimize=True)
        tint(m, LIGHT).save(BRAND / f"butterfly-sprite-light-{px}.png", optimize=True)
        (BRAND / f"butterfly-sprite-{px}.svg").write_text(sprite_svg(m, "#FF00F5"))

    # Favicon / app icons from the 32px sprite.
    m32 = sprite(alpha, 32)
    (APP / "icon.svg").write_text(sprite_svg(m32, "#FF00F5"))
    icon = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    big = tint(m32, MAGENTA).resize((160, 160), Image.Resampling.NEAREST)
    icon.alpha_composite(big, (10, 10))
    icon.convert("RGB").save(APP / "apple-icon.png")

    # Wordmark: black and white versions.
    wm = Image.open(SRC / "wordmark.png").convert("RGBA")
    wm = wm.crop(wm.getchannel("A").getbbox())
    a = wm.getchannel("A")
    for name, rgb in (("wordmark-black", INK), ("wordmark-white", (255, 255, 255))):
        img = tint(a, rgb)
        h = round(img.height * 1600 / img.width)
        img.resize((1600, h), Image.Resampling.LANCZOS).save(BRAND / f"{name}.png", optimize=True)

    # OG image 1200x630: wordmark + butterfly on white with a dither dot field.
    og = Image.new("RGBA", (1200, 630), (255, 255, 255, 255))
    dots = Image.new("RGBA", og.size, (0, 0, 0, 0))
    dp = dots.load()
    for y in range(8, 630, 16):
        for x in range(8, 1200, 16):
            for dx in (0, 1):
                for dy in (0, 1):
                    dp[x + dx, y + dy] = MAGENTA + (60,)
    og.alpha_composite(dots)
    bf = tint(alpha, MAGENTA).resize((420, 420), Image.Resampling.LANCZOS)
    og.alpha_composite(bf, (720, 105))
    w = tint(a, INK)
    w = w.resize((620, round(w.height * 620 / w.width)), Image.Resampling.LANCZOS)
    og.alpha_composite(w, (80, 315 - w.height // 2))
    og.convert("RGB").save(APP / "opengraph-image.png", optimize=True)

    # Portfolio photos.
    for f in sorted((SRC / "work").glob("*")):
        if f.suffix.lower() == ".heic":
            import pillow_heif  # noqa: PLC0415

            pillow_heif.register_heif_opener()
        img = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        img.save(WORK / f"{f.stem}.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        print(f"work/{f.stem}.jpg {img.size}")

    print("done")


if __name__ == "__main__":
    main()
