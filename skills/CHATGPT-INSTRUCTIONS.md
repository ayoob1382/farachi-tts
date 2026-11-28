# FARACHI Skills: ChatGPT Usage Instructions

Use the FARACHI skill guides as task-specific working instructions when this repository is connected and its files are accessible in the current conversation.

Repository: https://github.com/ayoob1382/farachi-tts
Skill index: `skills/README.md`
Registry: `skills/registry.json`

## Operating rule
Before a task involving motion graphics or video production, identify the relevant skill guides and read their `SKILL.md` files. Do not claim a skill was loaded if the file was not actually retrieved. If GitHub access is unavailable in this chat, ask the user to attach the relevant skill file or use a ChatGPT Project containing the skill documents.

## Skill selection
- Overall visual language: `motion-design`
- Object and shape animation: `2d-animation`
- Persian/Latin animated text: `kinetic-typography`
- Data visualization: `animated-charts`
- Process diagrams and visual explanations: `infographics`
- Narration-to-scene planning: `storyboarding`
- Frame layout and visual hierarchy: `composition`
- Motion rhythm and synchronization: `timing-easing`
- Scene changes: `transitions`
- Supporting visual effects: `visual-effects`
- Renderer implementation and validation: `video-rendering`

## Production workflow
For a complete video, normally apply Storyboarding first, then Motion Design and Composition, then the relevant scene-specific skills, Timing & Easing, Transitions, and Video Rendering. Preserve factual accuracy and the user's requested style. Tie visuals to narration meaning and timing. Avoid repeated short loops used to fill long durations. All time-based scene logic should be deterministic and seekable.

## Honesty and limitations
These files are project guidance, not executable software and not a modification of the GPT model. Repository access is not automatically available in every unrelated chat. Never imply global installation or automatic loading unless the platform explicitly confirms it.
