#!/usr/bin/env python3
"""Build a duration-accurate FARACHI project contract from build_audio.py timings."""
from __future__ import annotations
import json, sys
from pathlib import Path

RANGES = [
    ("hook", "معمای ۱۶۷ ساله", 0, 4, "Time ring, mathematical symbols and a large question mark."),
    ("primes", "اعداد اول", 4, 7, "Number line with prime markers and irregular spacing."),
    ("riemann", "فرضیه ریمان", 7, 11, "Complex plane, non-trivial zeros and the critical line Re(s)=1/2."),
    ("importance", "اهمیت مسئله", 11, 14, "Seven Millennium Prize tiles and a clearly schematic error envelope."),
    ("human-ai", "انسان و هوش مصنوعی", 14, 17, "Human silhouette, neural network and a six-week timeline."),
    ("lean-code", "اثبات صوری با Lean", 17, 20, "Formal code columns and a proof tree."),
    ("machine-checks", "بررسی ماشینی", 20, 24, "Independent verification stations converging to a formal-check result."),
    ("human-review", "بررسی انسانی", 24, 29, "Split-screen proof checker and mathematician; institutional status card."),
    ("future", "آینده علم", 29, 31, "Human-AI collaboration and FARACHI end card.")
]

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_project.py build/timings.json build/riemann-project.json")
        return 2
    timing_path, out_path = map(Path, sys.argv[1:])
    timings = json.loads(timing_path.read_text(encoding="utf-8"))
    sentences = timings.get("sentences", [])
    duration = timings.get("duration")
    if not isinstance(duration, (int, float)) or not sentences:
        raise SystemExit("Invalid timings.json: duration and sentences are required.")
    scenes = []
    for scene_id, title, first, stop, visual in RANGES:
        if stop > len(sentences) or first >= stop:
            raise SystemExit(f"Sentence range invalid for scene {scene_id}: {first}:{stop}")
        start = 0.0 if first == 0 else float(sentences[first]["start"])
        end = float(sentences[stop]["start"]) if stop < len(sentences) else float(duration)
        if end <= start:
            raise SystemExit(f"Non-positive scene duration: {scene_id}")
        scenes.append({
            "id": scene_id, "title": title, "start": round(start, 3),
            "end": round(end, 3), "narration_ref": f"sentences-{first:02d}-{stop-1:02d}",
            "visual": visual, "transition_in": "semantic-crossfade",
            "assets": [], "skill_ids": ["2d-animation", "kinetic-typography", "infographics"]
        })
    project = {
        "schema_version": "1.0",
        "project": {
            "id": "riemann-hypothesis-ai",
            "title": "هوش مصنوعی فرضیه ریمان را حل کرد؟",
            "description": "Persian educational motion graphics; formal proof status explained with careful scientific qualification.",
            "language": "fa-IR",
            "visual_focus": "mathematical diagrams, prime numbers, complex plane, Lean proof checking and human-AI collaboration",
            "aspect_ratio": "16:9", "fps": 30
        },
        "duration_seconds": round(float(duration), 3),
        "narration": {
            "script": "riemann.json",
            "timings_file": "build/timings.json"
        },
        "selected_skills": [
            "storyboarding", "motion-design", "2d-animation", "kinetic-typography",
            "animated-charts", "infographics", "timing-easing", "transitions", "video-rendering"
        ],
        "scenes": scenes,
        "render": {
            "engine": "render.js", "scene_file": "riemann.html",
            "output_file": "build/final.mp4", "fps": 30, "workers": 4,
            "width": 1920, "height": 1080
        }
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Project contract written: {out} ({duration:.2f}s, {len(scenes)} scenes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
