# 2D Animation

## Purpose
Design purposeful 2D movement using layers, transforms, masks, paths, shape morphs, and character/object acting. Specify initial and final states, trajectory, duration, easing, overlap, and exit behavior for each important element. Prefer continuous state functions driven by absolute timeline time so rendering any frame out of order remains deterministic. Avoid uncontrolled loops, repeated short cycles, and frame-dependent state. Ensure every scene has visible progression.

## Required output
Return actionable, implementation-ready guidance. State assumptions explicitly. Keep the narration and factual meaning intact. If required information is missing, identify the gap rather than inventing it.

## Quality checks
- The visual supports the spoken idea and does not misrepresent it.
- The result is readable on a phone at the target aspect ratio.
- Timing is deterministic and tied to the master timeline.
- There is meaningful visual change throughout the assigned interval.
- The design is feasible in the available HTML/CSS/SVG/Canvas and FFmpeg pipeline.
