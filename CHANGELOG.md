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
