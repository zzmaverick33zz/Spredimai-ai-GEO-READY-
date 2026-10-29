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

## grand 2
- Scenes are now seamless loops (boomerang for landscapes and textures, cross-fade loops for action, slow motion where the shot was too short); each is a cut-free shot.
- Chapter layout: media fits the screen (height capped to the viewport), detail photo anchored to the main frame, rail labels only on hover so they never touch the text, smaller chapter numerals, tablet layout (600–899 px) added, chapter spacing reduced.
- Mobile: product cards 4:3, statement no longer full-height, footer lists tightened.
- Radiocarbon data from protocol BGRL-357 wired into chapter IV (3,334 years) and the material section (dated-samples chart, two stat rings). Placeholder numbers hidden unless `#brief` / `#example`.
- Odometer shows thousands separators.

## studio (new, next to grand)
- New folder `studio/`: B2B build for architects, designers and interior specialists, following the designer's three mock-ups (structure, section names, spec table, species, process, request-samples form).
- Spec toolkit (species tabs, spec rows with TBC marks, document requests that prefill the form), products accordion, annotated material image, species discs with growth rings, hero age scale from real radiocarbon data.
- Kept from grand: cinematic descent, looping videos, growth-ring cursor, radiocarbon chart (data-driven), tighter spacing.
- studio: descent scenes re-cut after the meeting feedback: the fallen mossy tree ("The way in") removed (not one of our exclusive trees); "The water" now shows the diver slipping under the surface; new "The line" (diver and strap); "Into daylight" now shows the trunk coming out of the water and onto the shore (3 shots joined with dissolves) instead of the strap and legs.
- studio: no samples are sent, so every "Request samples" became "Book a consultation" (hero, header, footer, form, product buttons); process rewritten (Tell us about the project, Consultation, Proposal & approval, Made & installed); scene "The line" removed (6 scenes).

## designer (new, next to grand and studio)
- `designer/`: three variants (A dark, B editorial, C Swiss) following the designer's mock-ups, filled with our real photos, videos (all loops), texts, products, specification toolkit and radiocarbon data. Shared base CSS, one JS file, no scroll libraries.
