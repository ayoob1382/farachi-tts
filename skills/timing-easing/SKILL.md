# Timing & Easing

## Purpose
Set motion timing to support meaning and narration. Use anticipation, acceleration, deceleration, overshoot, settling, and stagger selectively. Avoid applying the same duration and easing to every element. Coordinate visual events with narration timestamps and leave enough hold time to read labels. Use absolute-time calculations and deterministic interpolation. Document start, end, duration, easing curve, and synchronization anchor.

## Required output
Return actionable, implementation-ready guidance. State assumptions explicitly. Keep the narration and factual meaning intact. If required information is missing, identify the gap rather than inventing it.

## Quality checks
- The visual supports the spoken idea and does not misrepresent it.
- The result is readable on a phone at the target aspect ratio.
- Timing is deterministic and tied to the master timeline.
- There is meaningful visual change throughout the assigned interval.
- The design is feasible in the available HTML/CSS/SVG/Canvas and FFmpeg pipeline.
