# FARACHI — Riemann Hypothesis / Production Blueprint

**Status:** render-ready first implementation  
**Branch:** `feat/farachi-motion-skills`  
**Canvas:** 1920×1080, 16:9, 30 fps  
**Duration:** derived from actual TTS timings; expected around 5–7 minutes, not hard-coded.

## Accuracy guardrails
- Never state that the Riemann Hypothesis has been officially accepted as solved.
- Say that a formal Lean proof was submitted/published and passed reported machine checks; human mathematical review and institutional recognition remain separate.
- The critical line is `Re(s)=1/2`.
- The prime-number and zeta visuals are explanatory diagrams, not empirical datasets.
- The seven Millennium Prize problems are represented as a conceptual list; the Riemann tile is highlighted, not a claim of prize payment.
- The approximate code-line count and six-week timeline are attributed to the public account/reporting and must remain qualified as approximate/reported.

## Visual system
- Background: deep navy `#080F20`; panels `#111D35`.
- Main accent: cyan `#55E6D2`; secondary: amber `#FFB45C`; warning: coral `#FF6F75`.
- Persian typography: RTL captions in a single lower-third panel; no per-glyph animation.
- Latin/math notation remains LTR in isolated labels.
- Motion is deterministic and derived from absolute `window.setTime(t)`.
- No remote assets, random motion, infinite CSS animations, or short loops stretched across the full duration.

## Scene map
Scene boundaries are derived from actual sentence timing indices by `prepare_project.py`.

| Scene | Sentence indices (0-based, end exclusive) | Visual concept | Main motion |
|---|---:|---|---|
| 01 Hook | 0–3 | Time ring, mathematical symbols, question mark | Radial reveal, accelerating number field |
| 02 Primes | 4–6 | Number line 1–30 | Prime markers illuminate; camera-like horizontal pan |
| 03 Riemann | 7–10 | Complex plane and critical line | Axes draw on; zeros appear on Re(s)=1/2 |
| 04 Why it matters | 11–13 | Seven Millennium tiles + schematic error band | One tile isolates; error envelope tightens |
| 05 Human + AI | 14–16 | Human silhouette, neural network, six-week timeline | Network grows; timeline fills |
| 06 Lean code | 17–19 | Formal code columns and proof tree | Code streams in finite staged groups; proof tree assembles |
| 07 Machine checks | 20–23 | Independent verification stations | Three stations validate; convergence to one result |
| 08 Human review | 24–28 | Split screen: proof checker vs mathematician; active-status card | Mechanical checks settle; human review remains in motion |
| 09 Future | 29–30 | Human/AI collaboration and FARACHI end card | Camera pullback; logo forms from connected points |

## Narration-to-visual synchronization
- Captions are populated from `build/timings.json`; each segment appears only during its actual spoken interval.
- Scene changes follow sentence indices, not fixed timestamps, so real TTS duration changes do not desynchronize visuals.
- Each chapter includes a 0.55-second crossfade. The previous and next scenes overlap intentionally.
- The scene groups contain different geometry and composition; no single short animation is repeated to fill the video.

## Render and QC
1. Run `build_audio.py riemann.json --out build` (real TTS) or `--fake` (timing/render test only).
2. Run `prepare_project.py build/timings.json build/riemann-project.json`.
3. Render `riemann.html` with `render.js`.
4. Mix audio and music with `mix.py`.
5. Run Quality Controller on the actual MP4 and timings.
6. Human-review representative frames from every scene and listen to the full narration. Automated pixel checks cannot judge mathematical meaning or aesthetic quality.
