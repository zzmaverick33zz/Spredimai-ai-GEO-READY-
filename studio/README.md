# Big Foot Floors: studio build (architects, designers, interior specialists)

Information architecture follows the designer's mock-ups: hero with spec CTAs, origin timeline, products accordion, applications, material (colour and age), six species, specification toolkit, process, projects, request samples.
The cinematic descent from the `grand/` build is kept as the story band. `grand/` itself is unchanged.

- Serve: `python3 serve.py` (http://localhost:8080/index.html) or open `dist/Big_Foot_Floors_Studio_HD.html`.
- `js/data/spec.js`: species, specification rows (`tbc: true` shows a TBC mark), documents. `js/data/samples.js`: radiocarbon examples. Edit only these to change content.
- `js/studio.js`: accordion, annotated image, species rings, spec tool (keyboard: arrow keys on the tabs), age scale, form prefill (document / product buttons write into the request form).
- Media briefs: `#brief`. `?static` = no motion.
- Single files: `python3 build_single.py hd` (full quality) and `python3 build_single.py light` (<16 MB).
