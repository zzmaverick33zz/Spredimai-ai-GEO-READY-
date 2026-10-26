# Big Foot Floors: final build

Plain HTML + CSS + JS (GSAP, ScrollTrigger, Lenis in `vendor/`). **Serve with `python3 serve.py`** (http://localhost:8080/index.html). `python -m http.server` has no HTTP Range support: browsers cannot seek video with it and the scroll-driven film stutters. Any real host is fine.

- Media briefs are off; add `#brief` to the URL for the team view. `?static` = no motion.
- Video: two quality tiers. `*-hd.mp4` (up to 1920 px) for viewports >= 1100 px, `*-sd.mp4` below, webm as a fallback for browsers without H.264. Rebuild from the originals: `python3 process_final.py` (needs `source-media/ultra`).
- `js/effects/`: `intro.js`, `film.js` (scroll controls the video, 24.5 s cut, 2.4 screens of scroll), `cursor.js` (dot + spring ring + label pill + magnetic buttons), `lift.js`, `counter.js`, `compare.js`, `progress.js`, `extras.js`.
- Header hides while scrolling down and returns on the first move up; a thin brass line shows page progress.
- `python3 build_single.py` writes `dist/Big_Foot_Floors_final.html` (one file, small video tier).
