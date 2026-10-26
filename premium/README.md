# Big Foot Floors: premium build

Plain HTML + CSS + JS (GSAP, ScrollTrigger, Lenis in `vendor/`).

**Run it with `python3 serve.py`** (opens on http://localhost:8080/index.html#clean). Do NOT use `python -m http.server`: it has no HTTP Range support, so browsers cannot seek or stream video, and the scroll-scrubbed film and video loops stutter. Any real web server (nginx, Netlify, Vercel, ...) is fine.

- `index.html` the page. `#clean` hides media briefs, `?static` turns motion off.
- `js/effects/`: `intro.js` (growth-ring preloader, once per session), `film.js` (scroll controls the video), `lift.js`, `counter.js`, `compare.js`, `progress.js`, `extras.js` (cursor ring, drifting numerals, contour lines).
- Performance rules used throughout: transform/opacity only while scrolling; no CSS masks, blend modes or backdrop blur over video; videos start only after the page has painted and are paused off-screen; nothing heavy downloads until it is about to appear.
- `python3 build_single.py` writes `dist/Big_Foot_Floors_premium.html` (one file, lite videos).
