# Big Foot Floors: grand build

Plain HTML + CSS + JS (GSAP, ScrollTrigger, Lenis in `vendor/`). **Serve with `python3 serve.py`** (http://localhost:8080/index.html) or open `dist/Big_Foot_Floors_HD.html` directly.

- **The descent** (`js/effects/descent.js`): seven single-shot films play at natural speed. Scroll never scrubs video; it only moves to the next scene, with a timed cross-dissolve. Pinned for about 0.46 screens per scene (0.4 on phones). Dots on the right jump to a scene. Reduced motion / `?static`: first scene poster.
- **Cursor** (`js/effects/cursor.js`): growth rings of a tree. A brass core follows exactly; irregular rings follow with a spring and slowly turn; hold still and rings grow (up to six), move and they draw back; press sends a ring out; `data-cursor` shows a tag. Mouse only.
- **The material** (`#material`, `js/effects/material.js`): tone swatches, two stat rings, dimensioned trunk, growth rings. All values are placeholders (see QUESTIONS 22). `#example` previews filled values (bogoak.fr reference, labelled NOT Big Foot data).
- **Scale**: type tokens enlarged (h1 up to 11.5 rem, h2 up to 7 rem, numerals up to 19 rem), full-screen manifest whose words light up as you scroll.
- Media briefs off; `#brief` shows them. `?static` = no motion.
- Video tiers: `*-hd.mp4` >= 1100 px, `*-sd.mp4` below, `*-hd.webm` fallback. Scenes: `python3 process_scenes.py [names]` (needs `source-media/ultra`).
- Single files: `python3 build_single.py hd` (full quality, ~45 MB) and `python3 build_single.py light` (<16 MB).
- Videos: every clip is a seamless loop made from ONE cut-free shot (the source film is cut every ~1-2.5 s). `process_scenes.py` (descent) and `process_loops.py` (hero and chapters). Radiocarbon figures: `js/data/samples.js` (edit only this file).
