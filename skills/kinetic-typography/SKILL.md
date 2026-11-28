# Kinetic Typography

## Purpose
Animate Persian and Latin text while preserving readability and correct shaping. Treat each phrase as a semantic unit; reveal, emphasize, rearrange, or transform text only to support the spoken point. Account for RTL direction, Persian joining, punctuation, line breaks, font fallback, and safe margins. Avoid splitting Persian words into independently moving glyphs unless shaping is preserved. Specify text, hierarchy, alignment, reveal method, timing, and hold duration.

## Required output
Return actionable, implementation-ready guidance. State assumptions explicitly. Keep the narration and factual meaning intact. If required information is missing, identify the gap rather than inventing it.

## Quality checks
- The visual supports the spoken idea and does not misrepresent it.
- The result is readable on a phone at the target aspect ratio.
- Timing is deterministic and tied to the master timeline.
- There is meaningful visual change throughout the assigned interval.
- The design is feasible in the available HTML/CSS/SVG/Canvas and FFmpeg pipeline.
