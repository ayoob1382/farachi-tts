# FARACHI Motion Skills

This directory contains original, project-specific skill guides for the FARACHI video workflow.

## Important
These are instruction files, not executable plugins and not a global installation into ChatGPT. They can be read by ChatGPT through the connected GitHub repository or included in a ChatGPT Project/custom instructions workflow. Availability in unrelated chats is not automatic.

## Skill set
- [FARACHI Animation Director](./farachi-animation-director/SKILL.md) — central director and orchestrator; use before planning a complete video.
- [Motion Design](./motion-design/SKILL.md)
- [2D Animation](./2d-animation/SKILL.md)
- [Kinetic Typography](./kinetic-typography/SKILL.md)
- [Animated Charts](./animated-charts/SKILL.md)
- [Infographics](./infographics/SKILL.md)
- [Storyboarding](./storyboarding/SKILL.md)
- [Composition](./composition/SKILL.md)
- [Timing & Easing](./timing-easing/SKILL.md)
- [Transitions](./transitions/SKILL.md)
- [Visual Effects](./visual-effects/SKILL.md)
- [Video Rendering](./video-rendering/SKILL.md)

## Use
Read the relevant `SKILL.md` before planning or implementing that part of a video. For a full production, start with FARACHI Animation Director. It directs Storyboarding, Motion Design, Composition, Timing & Easing, Transitions, Video Rendering, and the scene-specific skills as needed. Use Video Rendering for final implementation and validation.


## FARACHI Core

The first executable Core implementation lives in [`farachi_core/`](../farachi_core/README.md). It validates project briefs and timing files, reads this skill registry, and produces a deterministic skill execution plan. It does not execute AI skills or replace the existing renderer.
