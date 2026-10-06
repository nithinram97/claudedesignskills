# Clairvoyant brand kit (handoff for Claude Code)

Everything made so far for the **Clairvoyant** team's identity: the logo, the
**Orb** mascot, the animation stories and the Blender scripts. Read this file
first: it holds all the decisions, so you don't need the original chat.

**Context.** Clairvoyant is a team at Airbus (Bengaluru) that builds performance
dashboards in Skywise across business functions. The brand idea: *the moment a
measurement turns into foresight*. Data on its own looks back; the team's work
is seeing where it's going.

---

## 1. The logo

### What it means
| Element | Meaning |
|---|---|
| **Open C ring** | Reads as a crystal ball *and* the letter C at once. |
| **Gap on the right** | A crystal ball is closed; this one is open. The gap is where insight escapes. |
| **Thin inner ring** | Gives the sphere depth (drop it below ~32 px). |
| **Baseline + 4 rising bars** | The dashboards / KPIs. |
| **Amber 4th bar → breakout line → point** | The metric breaking out through the gap and becoming foresight. The only colour accent. |
| **V stand** | Holds the sphere up; doubles as a wing chevron / upward arrow (aerospace). |
| **Groundline** | Grounds it: instrument, not fortune-teller. |

### Exact geometry (SVG user units; every file is built from this)
```
open ring     path  M236 84 A56 56 0 1 0 236 146      stroke 12   (centre 190,115  r 56, gap ±34° facing right)
inner ring    path  M225 91 A42 42 0 1 0 225 139      stroke 2
baseline      line  152,150 -> 228,150                stroke 2, round caps
bars (rx 1)   x=158 y=132 w10 h18 | x=174 y=124 w10 h26 | x=190 y=116 w10 h34 | x=206 y=106 w10 h44 (AMBER)
breakout      line  211,106 -> 256,88                 stroke 3, round caps, AMBER
point         circle 258,87 r5                        AMBER
V stand       polyline 148,168 -> 190,210 -> 232,168  stroke 6, round caps/joins
groundline    line  158,218 -> 222,218                stroke 6, round caps
mark bbox     x 128..263, y 53..221
```
**Simplified mark** (use below ~32 px): ring stroke 16, no inner ring/baseline/bars,
breakout `211,118 -> 254,100` stroke 7, point `258,98 r8`, V stroke 9, groundline y 219 stroke 9.

### Colours
| Use | Light variant (on white) | Dark variant (on dark) |
|---|---|---|
| Mark + wordmark | Slate `#2F4356` | White `#FFFFFF` |
| Accent (amber bar, breakout, point) | Amber `#E8A33D` | Amber `#F5B942` |

Supporting: deep slate `#16202B` (backgrounds), ice `#CFE3F5` (glows),
data-blue `#5FA8E8` (chart bars before they turn brand-white). Single-colour
version: replace the amber hex with the slate (or white) one.

### Type
- **Wordmark: Michroma**, all caps, **7% tracking (0.07 em)**, colour = mark colour.
  It's **outlined to paths** in every SVG, so no font install is needed to use the files.
  Font files are in `font/` (SIL Open Font License: commercial use and outlining are allowed).
- **Body / taglines: IBM Plex Sans.** Never set long text in Michroma.
- Below ~14 px, set the name in IBM Plex Sans Medium, letterspaced, instead of Michroma.

### Lockups
- **Stacked:** mark centred over the wordmark (centre on the mark's *bbox* centre, x = 195.5),
  wordmark 40 px with the mark scaled 2.25x, gap 46 px between the mark bottom and the cap top.
- **Horizontal:** mark scaled 1.62x, 64 px gap, wordmark 52 px, vertically centred.
- Optional tagline: *"We don't chase the number. We see where it's going."* (IBM Plex Sans)

### Logo files (`logo/`)
- `svg/`: 8 masters. `clairvoyant-mark`, `-mark-simple`, `-lockup-stacked`, `-lockup-horizontal`, each in light and `-dark`.
- `png/`: the same 8 as **transparent** PNGs (lockups 2000-3000 px wide, mark 1024, simple 512).
- `icons/`: simplified mark at 32/64/128/256 px, light and dark (avatars, favicons).
- **The `-dark` files are white and look blank on a white background.** That's expected.

---

## 2. Orb, the mascot

The logo's sphere, alive. **Use in Slack, stickers, onboarding, videos. Never inside
the official lockup or on exec slides.**

- **Body:** a sphere, slate `#2F4356` (lift to `#46647F` in 3D, or it renders black).
  Glossy, with a cool rim light.
- **Eyes:** large, white `#F4F7FA`, dark pupils `#0B1118`, two white highlights each.
  Placed ±24° either side of centre, a little above the equator.
- **Brows:** short dark bars that tilt for expression (determined = inner ends down,
  worried = inner ends up and raised).
- **Cheeks:** blush ovals `#F28B82`.
- **Mouths:** smile, grin (open, with a pink tongue `#E86A6A`), small "o", flat line.
  Happy eyes = `^ ^` arcs.
- **Antenna:** amber stalk `#F5B942` from the upper right of the head, ending in a
  glowing amber **spark**. The spark *is* the logo's breakout point.
- **Legs:** two chunky legs (the logo's V) and bean-shaped feet (the groundline).
- **Personality:** curious, eager, a bit gormless, brave. He **feels every jump**:
  psych up (squint, brows down) → strain (wide eyes, "o") → brace (eyes shut) → relief (smile).

Files: `orb-character/` has 9 expressions as SVG + transparent PNG
(neutral, happy, surprised, determined, worried, glowing, spark-gone, running, jumping)
and `orb-character-sheet.png`.

### Story rules learned so far (keep these)
- **The line chart only ever goes up.** No dips, no falling spark. Weave in depth, never downward.
- **No decorative circles** (target rings, shockwave rings). The only circle is the logo's C.
- **Jumps must be physical:** parabolic arcs at constant horizontal speed, anticipation crouch,
  squash on landing. Never ease position keys in and out (that looked janky).
- Orb must never get stuck between bars or clip into them.
- Celebrate big: happy eyes, grin, cheeks glowing, sparkles, a spinning jump.

---

## 3. Stories

### A. "Orb chases the spark" (main film, ~19 s): `blender/clairvoyant_orb_chase_story_v2.py`
1. Idle; his antenna tip twitches, pops off and flies away drawing a **rising** line chart.
2. Bars grow out of the floor under the line; Orb runs and climbs them (the chart **is** the logo's 4 bars at 12x).
3. The biggest step: he lands on the edge of the amber bar and teeters.
4. The spark slowly draws the breakout line upward, out of reach; he jumps and falls short.
5. **Foresight:** eyes close, he glows, forecast dashes project *ahead* of the line.
6. He **outruns the line**, hopping along the forecast dashes, reaches the end first, waits.
7. The spark arrives and snaps back on: joy.
8. Reveal: the C ring draws round the chart, everything rises, the V and groundline emerge.
9. Orb melts into the breakout point; wordmark + tagline.

Storyboard (2D, an earlier pass of this story): `storyboards/chase-story/`.
Test renders of the v2 script: `renders/blender-v2-chase/`.

### B. "The big grin" transformation (~6 s, storyboard only): `storyboards/big-grin-transform/`
Orb grins wider and wider until the corner of his smile breaks through his cheek.
His body becomes the open C (**the gap is his grin**), his eyes drop in as two bars,
cheeks become the third bar, tongue the baseline, the amber bar rises, his antenna slides out
as the breakout line, legs swing into the V. A sparkle on the point is the last trace of his wink.
**Not built in Blender yet.**

### C. Earlier transformation (~14 s): `blender/clairvoyant_orb_transform_v1.py`
Orb lands on a data-grid stage, pillars rise, a halo forms; then the halo tightens into the C,
his legs fold into the V, the antenna spark flies to the breakout point, the body dissolves.
17 rendered key frames: `renders/blender-v1-transform/`.

### Other ideas in the pipeline
- **Orb riding a tiny Beluga** (plane only just big enough to sit on), weaving through bar-shaped
  obstacles while his spark draws a rising line chart: `illustrations/`. The user wants the
  obstacles to be something **other than buildings**. Options: cloud pillars, searchlight
  beams, stacks of cargo crates (the Beluga carries aircraft parts), upright fuselage/wing
  sections, rock spires, holographic data columns.
- Slack emoji set: `:orb-shipped:`, `:orb-looking:`, `:orb-that-metric-is-wrong:`,
  `:orb-oncall:`, `:orb-loading:`.
- Sidekick: the spark as its own little creature, **"Blip"**.
- Seasonal: Diwali (antenna = diya flame), birthday (antenna = candle), Santa hat.
- Other logo transformations considered: zoom into his eye (iris → C), spin into a ring,
  his shadow is the logo, paper-fold origami, x-ray reveal.

---

## 4. Blender scripts (`blender/`)
Self-contained Python. Tested on **Blender 5.2**, written for 4.2+, using EEVEE.
1. Open Blender, start a **new** General file and **save it** (output goes next to the .blend).
2. **Scripting** tab → Text → Open → pick the script → **Run Script** (Alt+P). It wipes the scene.
3. Camera view: **View → Cameras → Active Camera** (no numpad needed).
4. **Viewport shading → Rendered**, and in the shading dropdown set **Compositor → Always**,
   or everything looks grey (Solid mode shows no materials or glow).
5. **F12** = one frame, **Ctrl+F12** = MP4. For drafts set `RENDER_SAMPLES = 16`, `RES_X, RES_Y = 1280, 720`.

What's inside the scripts (reusable):
- Orb rig: sphere body, eyes with blink/look controls, brows, mouth set, happy eyes, blush,
  antenna + glowing tip, legs, feet. Squash pivot at the base of the body.
- **The official logo rebuilt in 3D** from the geometry above, plus **Michroma outlines embedded
  as Bezier data** (so the wordmark needs no font file).
- Stage: glossy data-grid floor, volumetric haze, floating motes, rim lights, bloom in the compositor
  (handles both the 4.x and 5.x compositor APIs), AgX colour.
- Jump helper `Choreo.hop()`: true parabola, anticipation, squash/stretch, expression beats.
- Beat timings are `F_*` constants at the top of the STORY section.

## 5. `tools/` (2D drawing scripts)
Python + cairosvg scripts that produced the storyboards and illustrations (the `orb()` 2D
drawing function lives in `orb_2d_storyboard.py`). **They contain absolute paths from the
original sandbox**; update the paths before running.
