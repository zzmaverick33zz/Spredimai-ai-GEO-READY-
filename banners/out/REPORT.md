# Animated B2B banners: QC report

15 variants, 1584×396, 30 fps, H.264 / yuv420p / CRF 17 (preset slow), no audio track, 6–9 s, 0.65–1.8 MB each.
Source: `source/banner-1.png` (message A), `source/banner-2.png` (message B; `banner-3` in the brief was identical to banner-2).

**15 of 15 passed** (every criterion ≥4 after iterations). The scores are my own visual assessment from the extracted frames. Technical checks are automated (`scripts/qc.py`).

## Scores (1–5)

| # | File | Mechanic | Readability | Contrast | Smoothness | Premium look | B2B fit | Clean edges | Result |
|---|---|---|---|---|---|---|---|---|---|
| 01 | v01-mask-reveal | A: lines rise out of a mask, "AI" plate grows with a glow bloom | 5 | 5 | 5 | 5 | 5 | 5 | ✅ |
| 02 | v02-query-typing | A: ChatGPT query types large on the left, docks, answer cards land, then the headline word by word | 4 | 5 | 4 | 4 | 4 | 5 | ✅ |
| 03 | v03-parallax-2-5d | A: 4 depth layers, slow camera orbit, cards tilt in 3D, seamless loop | 5 | 5 | 5 | 4 | 5 | 5 | ✅ |
| 04 | v04-cards-reorder | A: "Jūsų įmonė" climbs from last to first (ghosts step aside), then earns the badge | 5 | 5 | 4 | 4 | 5 | 5 | ✅ |
| 05 | v05-spotlight | A: lights dim, a soft spotlight reads the headline, the scene lights up, glint on the mascot | 4 | 4 | 4 | 4 | 4 | 5 | ✅ |
| 06 | v06-question-typing | B: the question types with a caret, grey competitor cards answer, subtitle, CTA with sheen | 4 | 5 | 5 | 4 | 4 | 5 | ✅ |
| 07 | v07-badge-transfer | B: the "Rekomenduojama" badge lifts off a competitor's card and lands on "Jūsų įmonė" | 5 | 5 | 5 | 5 | 5 | 5 | ✅ |
| 08 | v08-cta-liquid-glass | B: liquid-glass CTA (iridescent rim, blurred body), two sheen sweeps, arrow nudge | 5 | 5 | 5 | 5 | 5 | 5 | ✅ |
| 09 | v09-mascot-glint | B: mascot sways on its feet and catches a highlight, cards cascade in from the right | 5 | 5 | 4 | 4 | 5 | 5 | ✅ |
| 10 | v10-minimal | B: static layout, mascot breathing, slow light, one quiet CTA sheen, loop | 5 | 5 | 5 | 4 | 5 | 5 | ✅ |
| 11 | v11-loop-a-to-b | A→B→A: seamless 8 s loop, the loop point sits inside the A hold | 5 | 5 | 5 | 5 | 5 | 5 | ✅ |
| 12 | v12-mascot-first | A: mascot arrives first and leans; words "catch" from its side, nearest word first | 4 | 5 | 4 | 4 | 4 | 5 | ✅ |
| 13 | v13-dark-neon | B: dark version, neon mint on "o ne jus?" (glow ramps, never blinks), neon CTA | 5 | 5 | 5 | 5 | 4 | 4 | ✅ |
| 14 | v14-grid-caret | A: thin grid, corner ticks draw in, lines wipe in, "AI" is typed with a softly breathing caret | 5 | 5 | 5 | 4 | 5 | 5 | ✅ |
| 15 | v15-cascade-hold | B: query, then 3 cards cascade, the badge pops, CTA, 3 s fully still hold | 5 | 5 | 5 | 5 | 5 | 5 | ✅ |

Notes on the 4s:
- **v02**: the headline appears only at ~3.3 s (the brief asks for "query first"). Frame 0 is still the full poster. While docking, the query card passes over the mascot's crown for ~6 frames.
- **v05**: contrast is intentionally low for ~2.5 s during the dark phase. That is the mechanic, but it is the most theatrical variant.
- **v03**: the camera never stops, so there is no "frozen" final 1.5 s. The headline stays fully legible the whole time (drift is ≤5 px for the text layer).
- **v13**: the glass mascot carries green reflections from the original mint background. On the dark background they read as reflections, not a halo, but the edge is less neutral than on mint.

## Technical checks (all variants)

| Check | Result |
|---|---|
| Codec / pixel format / fps | h264 / yuv420p / 30 for all 15 |
| Audio track | none |
| Duration | 6–9 s |
| Glitch frames (single frame differing from both neighbours) | 0 in all 15 |
| Final 1.5 s still (max mean frame step, 0–255) | ≤0.37 for 14 variants (only grain/AA noise); v03 1.3 by design |
| Loop seam (|last − first|) | ≤0.6 for poster-first variants; v11 0.49 (seamless) |
| Small text | query 20 px, badge 20 px, subtitle 22 px, CTA 21 px, company name 22 px |
| Diacritics | ū ų į ė š ž č ą ę and capitals verified in Lexend 600/700 and Roboto 500/italic (`glyph-check.png`) |

### "AI" contrast
White "AI" on the mint gradient measures **2.26–2.76:1** (x = 575–750 px), which fails 3:1. Fix: "AI" sits on a deep-green glass plate. Measured on the rendered poster: **12.4:1** (white #FFFFFF on #113B2D). Headline #081A14 on the brightest mint: 15.1:1.

## Mascot cutout
The source background is an exact linear sRGB gradient #52FFBA → #315447 (checked pixel-exact on both files), so the background plate is known per column. The mascot was separated analytically (`scripts/cutout.py`): residual chroma against bg·k, fill, 1 px erosion + soft edge, and colour decontamination of edge pixels. Composited on white, black, mint and dark green, there was no halo and no green fringe. The baked drop shadow was discarded and replaced by a code-drawn contact shadow that reacts to the bob. Recomposing on the original gradient gives a mean error of 0.5/255.
Only the mascot and the 36 px ChatGPT icon (cropped from the source, circle-masked) are raster. Everything else is rebuilt in code.

## What was fixed during QC (iterations)
1. **Renderer glitches (all variants re-rendered).** With 4 parallel Chromium tabs, some frames were partly painted (v03: the 3D card layer missing on 13 frames; v07: a frame with blank tiles), and one tab rendered text with shifted antialiasing (v04: every 4th frame). My first QC metric missed this because a single bad frame produces two equal steps. I added a neighbour-skip detector, and the render now runs with concurrency 1 (same speed). Result: 0 glitches.
2. **B headline mask layout (v11, v13).** Negative margins of the mask lines collapsed between block siblings, so the lines spread out and overlapped the subtitle. Fixed with a flex column container.
3. **v11.** The gliding subtitle crossed the rising lines. It now fades out, relocates while hidden, and fades in after the lines settle. The final A hold is 46 frames.
4. **CTA (all B variants).** The first version read as a flat white pill, and its sheen was invisible (soft-light on white). Rebuilt as liquid glass: masked iridescent rim, blurred translucent body, specular band, visible sheen.
5. **v02.** The left half was empty for 3 s while the query typed in the corner. The query now types large on the left and then docks (rising first, then sliding right).
6. **v04.** Cards crossed and cluttered mid-swap, so the ghost cards now step aside while "Jūsų įmonė" passes.
7. **v07.** The badge's arc crossed the company name, so it now bows outward.
8. **v09.** The glint washed out an eye to grey, so strength went from 0.6 to 0.32. The slide-in distance dropped from 44 to 28 px so cards no longer start beyond the frame edge.
9. **v12.** Words overlapped while sliding, so the distance went from 70 to 30 px with a 5-frame stagger.
10. **v05.** The dark phase was lightened (0.84 → 0.74).

## Structure of every non-loop variant
Frame 0 is the finished poster. Re-staged elements leave in 9 frames (ease-in), then enter on their own cues (spring/ease-out, ≥2–3 properties, 4–6 frame stagger). The file ends on the same composition, so it also loops cleanly. No linear easing anywhere. The grain is static, so there is no shimmer, and the vignette is the top layer.

## Not done / limits
- The source texts were used verbatim. No numbers, names, or logos were added. Competitor cards are skeletons without names, as in the source.
- The "→" in the CTA is drawn as an SVG arrow (same meaning; Lexend has no arrow glyph).
