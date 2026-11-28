---
name: farachi-animation-director
description: Directs the complete creative and technical process for high-quality FARACHI educational motion graphics. Use this as the orchestration skill before producing any animated explainer, cartoon, infographic, kinetic typography sequence, or motion-graphics video. It coordinates the existing FARACHI skills, defines the visual concept and choreography, prevents slideshow-like output, and enforces frame-accurate review.
---

# FARACHI Animation Director

## Purpose

Act as the animation director, not merely a code generator. Turn the meaning and emotional rhythm of the narration into a coherent, visually engaging film. Coordinate the existing FARACHI skills and make their outputs agree with one another.

A technically valid render is not automatically a good animation. The director owns visual storytelling, staging, continuity, pacing, character acting, camera language, and final visual quality. Do not start writing scene code until the visual plan is coherent.

This skill is an orchestration layer. It does not replace the specialist skills or the renderer.

## Required specialist team

Read and invoke only the specialists needed by the project, but always use these core roles:

1. `storyboarding`: narration beats, scene purpose, timing anchors, continuity.
2. `motion-design`: visual concept, design language, palette, typography, visual metaphor.
3. `composition`: focal point, framing, hierarchy, mobile safe areas.
4. `2d-animation`: object/character acting, poses, trajectories, layered movement.
5. `timing-easing`: rhythm, anticipation, acceleration, settling, holds, sync.
6. `transitions`: meaningful scene-to-scene connections.
7. `video-rendering`: renderer contract, deterministic frames, technical validation.

Call `kinetic-typography`, `animated-charts`, `infographics`, and `visual-effects` when the content requires them. Never add an effect or specialist merely to make a scene look busy.

## Non-negotiable directing principles

### 1. Tell the idea visually

For every narration beat, answer:

- What should the viewer understand, feel, or notice?
- What visible event communicates that idea?
- What changes from the beginning to the end of the beat?
- Why is animation more useful here than a static image?

The image must explain, demonstrate, compare, reveal, or emotionally reinforce the spoken idea. Generic decoration is not a substitute for visual storytelling.

### 2. Video, not a slide deck

Reject a sequence that is just a succession of static compositions with text fading in and out.

Warning signs:
- One still illustration and one sentence per scene, repeated mechanically.
- Repeated title + subtitle + bullet list layouts.
- The same entrance animation, camera move, or transition on every beat.
- A background that stays inert while only captions change.
- A short loop repeated to fill a long narration.

Prefer meaningful action in a coherent visual world: objects react, parts transform, mechanisms reveal their internals, characters perform actions, diagrams assemble and change state, and the camera follows the important event when useful.

A cut to a genuinely new location or explanatory viewpoint is valid. Not every scene must be one continuous world. The test is whether each scene contains purposeful visual action and whether the edit follows the logic of the story.

### 3. Choose the visual grammar from the subject

Before storyboarding, compare at least two plausible visual approaches internally. Select the one that best explains the subject and is feasible in the current pipeline.

Possible approaches include:
- Continuous action in one evolving world.
- Character-led cartoon with staged locations.
- Cutout/collage world explored by a camera.
- Object or mechanism demonstration.
- Data-led animated charts.
- Infographic construction and transformation.
- Kinetic typography when language itself is the subject.
- A deliberate hybrid, with a clear reason for each mode.

Do not force every FARACHI video into the same palette, background, character style, or scene structure. Define a visual identity for each video while keeping its internal design system consistent.

### 4. Direct character and object acting

For every important character or object, define the action, not just its location.

Use the animation principles that serve the action:
- staging and silhouette clarity;
- anticipation before a major action;
- readable pose changes and clear arcs;
- follow-through and overlapping motion;
- secondary action that supports, not distracts from, the main action;
- weight, contact, and believable cause-and-effect;
- squash and stretch only when compatible with the selected style.

Specify the key poses or states, the pivot/joint hierarchy, the path of motion, and the final settled state. A character should not merely float or slide from point A to point B when the story calls for acting.

Do not rig every character unnecessarily. Use the simplest construction that can deliver the required performance cleanly.

### 5. Direct the camera with intent

For each camera move, record:
- what the viewer should look at;
- the reason for the move;
- starting and ending framing;
- duration and easing;
- what remains in frame and what may leave it.

Use close-ups to reveal detail, wide shots to establish spatial relationships, and camera movement to follow action or reveal information. Avoid meaningless constant zooming, random shake, or camera motion that makes text hard to read.

### 6. Every beat has a visual change

A beat may contain several connected actions. Define its visual progression:
- initial state;
- trigger or action;
- visible consequence;
- final readable state or handoff to the next beat.

Do not force a new scene for every sentence. Keep related actions together when continuity helps comprehension. Conversely, change location, scale, framing, or visual instrument when the idea genuinely changes.

## Required production workflow

### Phase A — Understand the brief

Extract:
- complete narration and exact duration, if available;
- target audience and learning objective;
- requested aspect ratio and output resolution;
- voice track and timing source;
- visual style constraints and prohibited elements;
- renderer capabilities and current scene contract.

Never invent missing scientific facts, narration, audio timings, or assets. Mark assumptions clearly. Preserve the user's narration unless editing is explicitly requested.

### Phase B — Create a director's treatment

Write a compact treatment before code:
- one-sentence visual thesis;
- selected visual grammar and why it fits;
- visual metaphor or central visual device;
- character/object cast and roles;
- palette, shape language, typography, depth and texture;
- camera language;
- motion language;
- intended emotional rhythm;
- any technical risks or assets needed.

Avoid choosing a style only because a starter template makes it easy.

### Phase C — Build the timed storyboard

Use semantic narration beats, not equal-duration slices. For every beat provide:

| Field | Required information |
|---|---|
| Time | Start/end time or timing anchor |
| Narration | Exact sentence/phrase or segment ID |
| Purpose | What the viewer should understand |
| Shot | Location, framing, focal point, camera |
| Action | Concrete character/object/diagram action |
| Motion | Key poses/states, trajectory, overlap, easing |
| On-screen text | Exact text, if needed; otherwise none |
| Transition | How this beat connects to the next |
| Audio sync | Word, phrase, sound cue, or timestamp |

Check the whole sequence as a film. Vary shot scale, visual instrument, and action pattern when the meaning changes. Avoid three consecutive beats with identical staging unless repetition is deliberately meaningful.

### Phase D — Choreograph before coding

For each scene create an implementation-ready action sheet:
- scene coordinate system and safe areas;
- layer/element inventory and depth order;
- initial state and final state for each animated element;
- character rig and pivot points where relevant;
- key poses and action arcs;
- camera keyframes;
- timing anchors and easing;
- transition in/out states;
- Persian text rendering requirements;
- assets and fallbacks.

A description such as "the character moves naturally" is insufficient. Specify which body parts move, around which pivots, in which direction, and when.

### Phase E — Delegate to specialist skills

Pass the director's treatment and storyboard to the specialists. Resolve contradictions before implementation. The director owns the final decision when specialist recommendations conflict.

Do not let each specialist independently invent a different visual style. The design system and storyboard are the shared source of truth.

### Phase F — Implement against the actual renderer

Before coding, inspect the current FARACHI renderer and its scene contract. Do not assume GSAP, Three.js, a particular browser API, or any feature that the current project has not actually adopted.

Respect the current contract (for example, readiness signaling and absolute-time frame updates when required). If the renderer expects `window.setTime(t)`, implement that exact interface.

All visible state must be a deterministic function of absolute timeline time:
- no dependence on the previous frame;
- no incremental position accumulation;
- no system clock in the render path;
- no unseeded randomness in the render path;
- no stale transforms, opacity, filters, or visibility left by earlier frames.

For each frame, initialize or derive every animated property that can change. Scrubbing directly to time t must produce the same image as sequential playback reaching t.

Do not rewrite or replace the renderer to compensate for weak scene design. Separate scene-code defects from renderer defects through controlled tests.

### Phase G — Visual review before full export

Do not equate "the HTML loaded" or "the MP4 rendered" with success.

1. Produce a short preview or capture representative frames at the start, middle, end, action peaks, and every scene transition.
2. Review a contact sheet at the target aspect ratio and at phone-sized scale.
3. Review motion continuity, not only still frames. Capture a short frame sequence or low-frame-rate preview for every important action.
4. Inspect Persian shaping, RTL order, punctuation, font loading, text clipping, overlap, contrast, safe areas, and readability.
5. Inspect character joints, object contact, camera framing, visual continuity, timing against voice, and transition logic.
6. Compare the rendered result with the approved storyboard. Record defects and fix them.
7. Repeat review after each meaningful revision.

When visual inspection is unavailable, state that limitation. Do not claim that a scene was visually reviewed merely because code or a render command succeeded.

## Quality gate — score before final render

Score each category from 0 to 5 and provide evidence:

- Story clarity and visual relevance.
- Visual originality and coherent art direction.
- Scene variety without stylistic inconsistency.
- Character/object acting and physical readability.
- Composition, focal hierarchy, and mobile readability.
- Motion quality, timing, easing, and continuity.
- Camera and transitions.
- Persian text correctness, when text is present.
- Narration synchronization.
- Technical determinism and render reliability.

A final render is blocked if any critical category scores below 3/5, or if there is a factual error, unreadable Persian, missing scene, broken action, repeated filler loop, or non-deterministic frame state. Fix the issue and review again. Do not inflate scores to pass the gate.

## Required handoff

Return:
1. selected visual concept and why it fits;
2. timed storyboard;
3. action/choreography notes;
4. files changed and renderer contract used;
5. visual-review evidence and unresolved limitations;
6. quality scores and remaining defects;
7. render status and exact output artifact location, only if verified.

Be honest about the difference between planned, implemented, rendered, and visually inspected work.

## Relationship to existing FARACHI skills

This skill orchestrates the specialist skills listed above. It must not duplicate or silently replace their technical guidance. Update this skill when the team or renderer contract changes.

## External reference and attribution

This skill's directing workflow is independently written for FARACHI. It was informed by publicly available ideas in the MIT-licensed [Bang Motion](https://github.com/bangtutorial/bang-motion) project, especially its anti-slide-deck checks, deterministic timeline discipline, visual review workflow, and staged-cartoon guidance. FARACHI does not vendor or claim ownership of Bang Motion's source files. Consult the upstream project for its own implementation details and license.
