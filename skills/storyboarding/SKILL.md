# Storyboarding

## Purpose
Translate the complete narration into a timed visual plan. Break narration at meaningful semantic beats, not arbitrary equal intervals. For every beat provide narration excerpt or segment ID, purpose, scene composition, on-screen elements, animation, transition, and approximate timing. Vary visual approach when the idea changes. Ensure no long narration span is covered by an unrelated static visual. Maintain continuity where scenes share objects or locations.

## Required output
Return actionable, implementation-ready guidance. State assumptions explicitly. Keep the narration and factual meaning intact. If required information is missing, identify the gap rather than inventing it.

## Quality checks
- The visual supports the spoken idea and does not misrepresent it.
- The result is readable on a phone at the target aspect ratio.
- Timing is deterministic and tied to the master timeline.
- There is meaningful visual change throughout the assigned interval.
- The design is feasible in the available HTML/CSS/SVG/Canvas and FFmpeg pipeline.
