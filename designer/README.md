# Big Foot Floors: designer variants (A, B, C)

Our real photos, videos, texts and products, laid out as in the designer's three mock-ups. `grand/` and `studio/` are not touched.

- `a.html` dark, uppercase grotesk · `b.html` light editorial serif · `c.html` Swiss grid. `index.html` links them.
- Serve with `python3 serve.py` (http://localhost:8080/). One shared `css/base.css`, one theme file per variant, one `js/site.js` (no GSAP, no scroll library).
- `build.py` generates the three pages from one content set (text, media names, species, products). Edit it and run `python3 build.py`.
- Content data: `js/data/spec.js` (specification rows, `tbc` marks, documents), `js/data/samples.js` (radiocarbon examples).
- Single files: `python3 build_single.py hd a` (also `b`, `c`; `light` for the small version).
- Copy rules kept from before: no invented facts (designer figures that are not confirmed are marked TBC or left out), consultation instead of samples, "water" instead of "river" (client: lakes and peat bogs).
