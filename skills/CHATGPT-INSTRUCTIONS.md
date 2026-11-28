# FARACHI Skills: ChatGPT Usage Instructions

Repository: https://github.com/ayoob1382/farachi-tts
Branch: `feat/farachi-motion-skills`
Skill index: `skills/README.md`
Registry: `skills/registry.json`

## Copy this block into ChatGPT Custom Instructions

When I ask for motion graphics, animation, visual storytelling, or video production, use the FARACHI skill guides as working instructions. The guides are stored in the GitHub repository `ayoob1382/farachi-tts`, branch `feat/farachi-motion-skills`, under `skills/`.

First check whether the GitHub connector is available in this chat. If it is, read `skills/registry.json` and retrieve the relevant `SKILL.md` files before doing the task. Select skills based on the request. For a full video, always read and use `farachi-animation-director` first. It orchestrates Storyboarding, Motion Design, Composition, the relevant scene-specific skills, Timing & Easing, Transitions, and Video Rendering.

If GitHub is not available in this chat, do not pretend to have read the skills. Tell me that repository access is unavailable and ask me to open the FARACHI GitHub connector or provide the skill files. Do not invent skill contents.

Keep visuals tied to the meaning and timing of narration. Preserve factual accuracy, Persian RTL text shaping, phone readability, and deterministic absolute-time animation. Do not fill long durations by repeating a short loop. Before rendering, inspect the scene plan for meaningful visual variation and verify the actual renderer contract from the repository.

These skill documents are project instructions, not executable plugins and not a modification of the GPT model. Do not claim they are globally installed or automatically loaded unless the platform confirms that.

## How to enable the instructions

1. Open ChatGPT Settings.
2. Open Personalization, then Custom Instructions.
3. Paste the block above into the field for instructions about how ChatGPT should respond.
4. Save the changes.

The Custom Instructions text only tells ChatGPT when and how to use the guides. It does not grant GitHub access. In each new chat, the GitHub connector must be available and authorized for the assistant to retrieve the files.

## Skill selection

- Central creative direction and orchestration: `farachi-animation-director` (read first for every complete animation/video task)

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

For a complete video, apply FARACHI Animation Director first. It then orchestrates Storyboarding, Motion Design and Composition, the relevant scene-specific skills, Timing & Easing, Transitions, and Video Rendering. Preserve factual accuracy and the user's requested style. Tie visuals to narration meaning and timing. Avoid repeated short loops used to fill long durations. All time-based scene logic should be deterministic and seekable.
