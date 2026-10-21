# Big Foot Floors: bog wood site (prototype)

Vite + vanilla JS, GSAP/ScrollTrigger, Lenis.

```bash
npm install
npm run dev        # development
npm run build      # -> dist/
npm run preview    # serve dist/
```

- `#clean` in the URL hides the media briefs. `?static` renders the page with no motion (for design import, e.g. html.to.design: open `/?static#clean`).
- Form: set `VITE_FORM_ENDPOINT` in `.env` (see `.env.example`). Empty means a stub that sends nothing.
- Media: `python3 scripts/process_media.py` rebuilds `public/media/` from `source-media/` (not in git). A slot gets real media from `public/media/manifest.json`; slots missing there show a text placeholder. The hero (S01) is written into `index.html` for LCP.
- Docs: `MEDIA_MAP.md` (what media is used where, shot list, retouch list, generation prompts), `QUESTIONS.md` (for the client), `CHANGELOG.md`.

## 3D beats
`src/js/scene.js` (Three.js) draws one trunk that turns, opens, becomes boards and then a floor, driven by scroll across six `.beat` sections. Textures in `public/media/3d/` are cut from the client's photos: `python3 scripts/make_textures.py`. It loads only when the first beat is near, and is hidden under reduced motion, `?static`, no WebGL and data saver. `AUDIT.md` has the reasoning and the limits.
