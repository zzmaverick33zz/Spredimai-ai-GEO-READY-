# Changelog

- Stack: Vite + vanilla JS, GSAP/ScrollTrigger, Lenis. CSS and JS moved out of `index.html`; tokens kept in `:root`. Palette, fonts and narrative unchanged.
- Chapter grounds are now tweened on `<body>` by scroll (instead of hard edges) when JS runs; without JS the original solid grounds remain.
- Copy: removed or softened claims not confirmed on bffloors.com: "most sustainable timber we know", "This is where most of the time goes", "fly in to install", "finest European and American species", Bog Ash "lighter, more silvered tone", Bog Oak "smoked brown to near black".
- Added `public/media/manifest.json`: slots take real media from the manifest; missing slots keep placeholder + brief.
- Added SEO: OG/Twitter meta, JSON-LD (Organization, LocalBusiness showroom, Product Bog Oak), `llms.txt`, `robots.txt`.
- QA fixes: pin is created before other ScrollTriggers; hero paragraph no longer fades in (LCP 3.0 s -> 1.4 s); Google Fonts load non-blocking; h4 -> h3 for heading order; products and forest species grids have no orphan cells at 760-1079 px; touch targets >= 44 px.
- Media wired: S01–S09 use real client photos/video (see MEDIA_MAP.md). Videos load only when they scroll into view. Remaining slots show text placeholders.
- `?static` mode (no motion) added for design import and screenshots.
- Focus ring on form fields.
- From bffloors.com: project countries (Norway, Switzerland, France, Germany, Cyprus, USA) in Projects; footer column linking to the current site's pages.
- Content from bffloors.com: copy aligned (most sustainable and rare wood, craftsmen fly in, design/stain/pattern, privacy note on projects, showroom email); 25 site photos wired into S03, S09–S31; client's message shown as a quote.
- Fonts: body/UI Montserrat -> Hanken Grotesk (Montserrat is generic and wide next to Garamond-style Cormorant); Cormorant kept for display. See AUDIT.md.
- Motion: six 3D beats (Three.js) between chapters, headings reveal word by word, photos open like a curtain, hero silt particles, film grain. Beats use `position: sticky`, not pins; reduced motion, `?static`, no WebGL and data saver hide them. Departs from the "minimal motion" brief at the client's request.
- Single-file build (`scripts/make_single_html.py`) inlines the 3D chunk and textures.
- 3D trunk rebuilt from the reference trunk photo (scripts/scan_trunk.py): scanned outline and ragged butt, photo projected as bark, mirrored beyond the visible side. Sling, chains and drips removed. First frame is the cleaned photo itself, handed over to the 3D mesh, which turns on a turntable.

## grand (after "final")
- Replaced the scroll-scrubbed film by **The descent**: seven single-shot scenes, natural-speed playback, scroll only changes scene (timed dissolve + slow push-in), huge captions, relative depth gauge, scene dots, pointer parallax.
- New cursor: growth rings (replaces the dot + ring + pill).
- Grandeur pass: larger type scale, full-screen manifest with word-by-word reading, bigger chapter spacing, enlarged section headings.
- New **The material** infographic (tones, stat rings, trunk dimensions, growth rings) with placeholder values.
- Single file now ships the **HD video tier** (`Big_Foot_Floors_HD.html`); light build for web preview.
