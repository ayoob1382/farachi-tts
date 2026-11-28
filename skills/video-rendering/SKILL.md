# Video Rendering

Prepare deterministic, render-ready scenes for the FARACHI pipeline. Confirm the scene contract expected by render.js, including readiness signaling and absolute-time frame updates. Match output aspect ratio, resolution, frame rate, duration, and asset paths to the job configuration. Avoid network-dependent assets at render time. Validate fonts, RTL text, missing assets, console errors, frame coverage, and audio/video duration. Run a short preview before a full render and inspect representative frames across every scene.

**Deliver:** render configuration, scene contract checklist, preview plan, and validation report.

**Quality checks:** scene readiness resolves, seeking is deterministic, all scenes render, audio/video durations match, and output file is playable.