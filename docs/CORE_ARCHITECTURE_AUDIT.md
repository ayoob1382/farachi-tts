# FARACHI Core — baseline audit

Audit target: `feat/farachi-motion-skills`

## What exists before the Core implementation

| Area | Existing component | Verified behavior / contract |
|---|---|---|
| Skill catalogue | `skills/registry.json` | 11 registered skills; all currently marked `draft` |
| Skill instructions | `skills/*/SKILL.md` | Human/agent guidance; not executable plugins |
| Voice generation | `build_audio.py` | Writes `voice.wav` and `timings.json` |
| Timing output | `build_audio.py` | Root object contains `duration`, `title`, and `sentences[]`; each sentence has `start`, `end`, `text` |
| Scene rendering | `render.js` | Loads an HTML scene, waits for `window.ready === true`, calls `window.setTime(t)` at deterministic frame times, reads `timings.json` from the build directory |
| Audio/video mix | `mix.py` | Combines voice, music, silent MP4, and timing data |
| CI entry points | `.github/workflows/make-video.yml`, `test-motion.yml` | Existing video workflows; test-motion checks the separate validation branch |

## Missing before this change

- No executable `farachi_core` package was present in the inspected branch.
- No shared project JSON schema was present.
- No automated tests for skill routing or the project/timing contracts were present.
- No Quality Controller existed to inspect scene contracts, timeline gaps/overlaps, or final render metadata.
- No `config/settings.json` exists in this branch's tracked tree. Do not assume the earlier Colab Drive configuration is part of this Git branch.

## Boundaries introduced

1. The Core validates a common project brief and the timing file produced by the current audio builder.
2. The Skill Manager reads the existing registry/manifests, resolves declared dependencies, and emits a deterministic execution plan.
3. Skill guides remain instructions. The manager does not claim to execute an LLM or run a skill autonomously.
4. `render.js` remains the renderer. The Core records its existing `window.ready` / `window.setTime(t)` contract and does not replace it.
5. The initial implementation is deliberately additive: existing audio, render, and mix scripts are not modified.

## Current pipeline boundary

```text
project JSON
    |
    v
FARACHI Core: validate project + load skill registry
    |
    v
Skill Manager: ordered execution plan (guide references)
    |
    |  Human/agent performs the planned creative passes
    v
HTML scene + build_audio.py output
    |
    v
render.js + timings.json -> silent MP4
    |
    v
mix.py -> final MP4
```

## Next engineering gates

- Run `python -m unittest discover -s tests -v` (also enforced by `.github/workflows/test-core.yml`).
- Validate a real project brief and a real `build/timings.json` from a workflow artifact.
- Exercise the Quality Controller against real scene HTML and final MP4 outputs; its static and pixel-sample checks are heuristics, not semantic review.
- Add a human frame/audio review gate and a documented approval record before calling a render production-ready.
- Do not mark the 11 skills production-ready until their procedures have been tested against actual scenes and outputs.
