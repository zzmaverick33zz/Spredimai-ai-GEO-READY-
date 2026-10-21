# Animated banners (Remotion)

15 animated 1584×396 banners built from `source/banner-1.png` / `banner-2.png`. Results and QC: `out/REPORT.md`, `out/contact-sheet.png`.

```bash
npm install
python3 scripts/cutout.py source/banner-2.png public   # mascot cutout (already in public/)
node scripts/meta.mjs                                   # variant list -> work/variants-meta.json
node scripts/render.mjs [v01 v02 ...]                   # out/vNN-*.mp4 + out/vNN-poster.png + QC frames
python3 scripts/montage.py v01 && python3 scripts/qc.py && python3 scripts/contact_sheet.py
npx remotion studio src/index.ts                        # preview
```

Uses the full Chromium at `/opt/pw-browsers/chromium` (chrome-for-testing mode) so Google Fonts load through the proxy CA. Render concurrency is 1: parallel tabs produced partially painted frames.
Code: `src/lib` (background, mascot, cards, headlines, animation helpers), `src/variants` (A1/A2 = message A, B1 = message B).
