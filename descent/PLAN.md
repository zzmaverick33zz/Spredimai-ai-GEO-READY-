# The Descent: plan (step 0 result)

## Done in step 0
- `Big_Foot_Floors_v1.html` copied from `out/versions/bigfoot-floors-v1-before-3d.html`.
- 34 embedded blobs (28 webp, 3 jpg, 3 mp4) extracted to `media/` (5.6 MB, map in `media/_manifest.json`). Page is pixel-identical before/after (0 differing pixels at 7 scroll positions, 1440 and 390 wide, JS off). Commit 17d9121.
- Structure: header.hdr, nav.rail, section.hero#top, section.statement#intro, article#ch1..#ch8 (data-g silt/deep/peat/char/oak), section.interlude#ch3, section.arrival, #collection, #products, #projects (4x article.proj), #heritage, section.care, #consult, footer.ftr. 31 slots S01-S31. Scripts: JSON-LD, one 143 KB minified Vite module (GSAP, ScrollTrigger, Lenis and the page logic bundled together).

## Blockers
1. 21st.dev is blocked by the session's network policy (403) and API_KEY_21ST is not set, so no component source could be installed or read. The sandbox (`_21st-sandbox/`) is therefore not built.
2. three.js CDNs are blocked, but npm works: three will be vendored locally from npm, pinned.

## Selectors per effect
| # | Effect | Hooks | Notes |
|---|---|---|---|
| 1 | Water ripple | `.hero .slot[data-slot=S01]` (picture/img), weaker on `#ch1 [data-slot=S02]` | WebGL plane, texture = the img; img stays in DOM; off for touch, reduced motion, no WebGL |
| 2 | Diver's torch | `#ch2 [data-slot=S03]`, `[data-slot=S04]`, `#collection .sp [data-slot=S14..S19]` | dim layer on top with radial mask, lit copy below; touch: Lissajous drift |
| 3 | The lift | `#ch3.interlude` (existing pin) + `.arrival` | layers at different scales, pointer drift, backdrop crossfade; see question 3 |
| 4 | Carbon counter | `#ch4 .chapter__text` (new block), `#heritage .fact b` (3rd, 20+) | placeholder constant only |
| 5 | Compare slider | `#ch5` S07 / S08 (S08 vs S11 until real photos) | role=slider, arrows/Home/End |
| 6 | Progress and depth | `.rail` (+ progress line, depth gauge), `#ch5` cross-section SVG rings | placeholder depths |

## Technical proposal
Keep plain HTML/CSS/JS. Replace the minified bundle by readable files: `vendor/` (gsap, ScrollTrigger, lenis, three from npm), `app.js` (v1 page logic restored from commit d6ebd89), `effects/*.js` (one file per effect). Final deliverable can still be re-inlined into one HTML.
