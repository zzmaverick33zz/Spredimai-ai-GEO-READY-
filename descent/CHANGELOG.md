# The Descent: changelog

Base: `Big_Foot_Floors_v1.html` (v1, before the 3D experiments). Plain HTML + CSS + JS, GSAP 3 + ScrollTrigger + Lenis (now in `vendor/`). Copy, section order, ids, JSON-LD and design tokens are unchanged. Media placeholders (`.slot`, `data-slot`, `.brief`, REPLACE comments) are kept.

Run: `python3 -m http.server` in this folder, open `/Big_Foot_Floors_v1.html#clean` (`#clean` hides the media briefs, `?static` turns all motion off).

## Structure changes
- Embedded base64 media extracted to `media/` (map: `media/_manifest.json`); render is pixel-identical (0 px diff at 7 scroll positions, 1440 and 390).
- The minified bundle is replaced by readable scripts: `vendor/` (gsap, ScrollTrigger, lenis), `js/core.js` (helpers, `BFF.fx` registry), `js/app.js` (page logic as in v1), `js/effects/*.js` (one file per effect), `css/effects.css`.
- Images are `loading="lazy"` except the hero, hero image has webp 800/1400 variants + preload, videos `preload="none"`. Keyboard fix: chapter text reveals use opacity only (v1 used autoAlpha = `visibility:hidden`, which hid focusable content until scrolled into view).

## Effects
| # | Effect | File | Hooks / selectors | `data-` options | Fallbacks |
|---|---|---|---|---|---|
| 1 | Water ripple | `js/effects/ripple.js` | `[data-ripple]` on `.slot` S01 (hero) and S02 (chapter I, weaker) | `data-ripple-frequency` (14), `data-ripple-amplitude` (0.012), `data-ripple-speed` (0.6) | reduced motion, coarse pointer, no WebGL, or a texture the browser refuses (e.g. cross-origin / `file://`) -> plain `<img>`, no canvas. Rendering pauses off-screen. |
| 2 | Diver's torch | `js/effects/torch.js` | `[data-torch]` on S03, S04, S14-S19 | `data-torch-radius` (px), `data-torch-dim="light"` for pale sections | reduced motion: no scrim. Touch / idle: Lissajous drift, finger follows on press. Never covers copy. |
| 3 | The lift | `js/effects/lift.js` | `#ch3.interlude` (+ `.lift__sky`, `.lift__spray` layers added at runtime) | none | below 900 px no pin (as in v1), layers still scrub. Reduced motion: v1 static section. Ground still `--deep` -> `--peat`; warm daylight is a glow that peaks during the lift (keeps the dark -> light order). |
| 4 | Carbon-dating counter | `js/effects/counter.js` | `#ch4 .dated[data-years]`, `#heritage .fact b` (3rd, 20+) | `data-years` (digits only) | **No age is invented**: `data-years` is empty, digits settle on dashes, visible TODO in brief mode. Reduced motion: final state, no tick. `aria-label` carries the final value once, `aria-live="off"`. |
| 5 | Before / after | `js/effects/compare.js` | `.compare[data-compare]` in `#ch5` | `data-start`, `data-hover="true"`, `data-orientation`, `data-label-before/after` | Works without motion. Pointer drag, hover-follow (mouse only), arrows move 2 %, Home/End, `role="slider"`, brass focus ring. Uses S08 vs S11 until real photos exist. |
| 6 | Progress, depth, rings | `js/effects/progress.js` | `.rail` (gauge), `[data-slot=S08]` (rings) | none | Depth gauge is RELATIVE (Surface / Deep) with TODO depths; no metres shown. Rings: `stroke-dashoffset` draw on scroll, drawn complete under reduced motion. |

## 21st.dev: what could and could not be obtained
`21st.dev` is reachable, but component source is behind `API_KEY_21ST` (the install endpoint answers 403 "authentication required") and the key was not available. Only the public `.md` listings could be read (saved in `_21st-notes/`). No component source was installed or read, so **nothing was ported from source**; every effect is a new implementation of the documented behaviour.

| # | Effect | Component(s) referenced | How it was built | Not obtained |
|---|---|---|---|---|
| 1 | Water ripple | Ripple Distortion (ruixen.ui, license unknown) | Re-written from its documented behaviour (frequency / amplitude / speed, concentric ripples at the cursor); raw WebGL instead of three.js | shader source, `_21st-sandbox` |
| 2 | Torch | Torch Reveal (rmahammad, MIT) | Re-written from behaviour (soft mask follows cursor with lag) | source |
| 3 | The lift | Zoom Parallax (efferd, unknown), Depth Parallax Scene (rmahammad, MIT) | Re-written on GSAP scrub; layered scales + pointer drift | source of both |
| 4 | Counter | Number Ticker (unknown), Odometer Numbers (MIT) | Re-written: per-digit rolling strips, left digit starts first | source |
| 5 | Compare | Image Compare (mohammadshehadeh, MIT) | Re-written from documented props (drag, hover-follow, keyboard, orientation) | source, so it is not a close port |
| 6 | Progress | Scroll animated timeline (ibrandify, MIT) | Own implementation; gauge and rings are custom | source |

A close MIT port needs the sources: set `API_KEY_21ST`, run the install commands from the brief in `_21st-sandbox/`, and the effects can be compared / replaced one by one.

## Checks (Playwright + Lighthouse, local server)
- Console errors: none at 1440x900, 390x844, reduced motion. No horizontal scroll.
- Lighthouse mobile: Performance 90-95, Accessibility 100, Best practices 100, CLS 0.001, LCP 2.6-3.5 s (simulated throttling; the hero image is preloaded).
- Reduced motion verified by emulation: no ripple, torch, pin, Lenis, counting; chapter grounds and all content visible.
- Keyboard: Tab reaches the compare slider (arrows, Home, End work), every stop shows a focus outline.

## Ultra media (client Drive)
S01, S03, S04, S05, S10, S11, S12, S13 are now video from the 1080p originals; S02, S20, S21 stills from them (process_ultra.py, MEDIA_MAP.md section 8). The hero ripple reads the video as its texture. The single-file build uses the -lite mp4.
