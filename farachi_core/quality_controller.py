#!/usr/bin/env python3
"""FARACHI Quality Controller: structural, timeline, scene and render audits.

Static checks are heuristics, not a substitute for watching the finished video.
The controller never edits project assets or silently changes a render.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .skill_manager import CoreError, _read_json, validate_project, validate_timings


def finding(items: list[dict[str, str]], severity: str, code: str,
            message: str, recommendation: str = "") -> None:
    row = {"severity": severity, "code": code, "message": message}
    if recommendation:
        row["recommendation"] = recommendation
    items.append(row)


def _safe_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def audit_timeline(project: dict[str, Any], report: list[dict[str, str]]) -> None:
    scenes = project.get("scenes", [])
    duration = project.get("duration_seconds")
    if not isinstance(scenes, list) or not scenes or not isinstance(duration, (int, float)):
        return
    valid = [
        s for s in scenes
        if isinstance(s, dict)
        and isinstance(s.get("start"), (int, float))
        and isinstance(s.get("end"), (int, float))
        and s.get("end") > s.get("start")
    ]
    if len(valid) != len(scenes):
        return
    ordered = sorted(valid, key=lambda x: (x["start"], x["end"], x.get("id", "")))
    if ordered[0]["start"] > 0.25:
        finding(report, "warning", "TIMELINE_HEAD_GAP",
                f"Timeline starts at {ordered[0]['start']:.2f}s; the opening may be uncovered.",
                "Cover the opening with an intentional visual or explicitly document the opening pause.")
    for previous, current in zip(ordered, ordered[1:]):
        gap = current["start"] - previous["end"]
        if gap > 0.25:
            finding(report, "warning", "TIMELINE_GAP",
                    f"Unassigned visual gap of {gap:.2f}s between {previous.get('id')} and {current.get('id')}.",
                    "Add a scene or make the pause an explicit storyboard decision.")
        elif gap < -0.10:
            finding(report, "error", "TIMELINE_OVERLAP",
                    f"Scenes {previous.get('id')} and {current.get('id')} overlap by {-gap:.2f}s.",
                    "Resolve the overlap or represent the intended compositing explicitly.")
    tail = duration - ordered[-1]["end"]
    if tail > 0.5:
        finding(report, "warning", "TIMELINE_TAIL_GAP",
                f"The final scene ends {tail:.2f}s before the project duration.",
                "Extend the closing visual or document the intentional end card/hold.")
    elif tail < -0.10:
        finding(report, "error", "SCENE_AFTER_DURATION",
                f"The final scene extends {-tail:.2f}s beyond project duration.")


def audit_scene_html(path: Path, report: list[dict[str, str]]) -> None:
    if not path.is_file():
        finding(report, "warning", "SCENE_FILE_MISSING",
                f"Scene HTML not found: {path}",
                "Provide the render-ready scene file when running the scene audit.")
        return
    source = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"window\s*\.\s*ready\s*=\s*true", source):
        finding(report, "error", "SCENE_READY_CONTRACT",
                "Scene does not visibly set window.ready = true.",
                "Set window.ready = true only after fonts, assets and scene initialization are complete.")
    if not re.search(r"window\s*\.\s*setTime\s*=", source):
        finding(report, "error", "SCENE_SETTIME_CONTRACT",
                "Scene does not define window.setTime(t).",
                "Implement absolute-time frame updates; render.js seeks frames out of order across workers.")

    nondeterministic = [
        (r"\bsetInterval\s*\(", "setInterval"),
        (r"\brequestAnimationFrame\s*\(", "requestAnimationFrame"),
        (r"\bsetTimeout\s*\(", "setTimeout"),
        (r"\bMath\s*\.\s*random\s*\(", "Math.random"),
    ]
    for pattern, label in nondeterministic:
        if re.search(pattern, source):
            finding(report, "warning", "SCENE_NONDETERMINISM",
                    f"Scene contains {label}; this can make frame-by-frame seeking inconsistent.",
                    "Derive every animated property from the absolute time passed to window.setTime(t).")

    if re.search(r"(?:animation-iteration-count\s*:\s*infinite|animation:\s*[^;]*\binfinite\b)", source, re.I):
        finding(report, "warning", "SCENE_INFINITE_CSS",
                "Scene contains an infinite CSS animation that may not follow the renderer's absolute timeline.",
                "Drive the motion from setTime(t), or explicitly synchronize the CSS animation to absolute time.")

    if re.search(r"\b(?:while|for)\s*\(\s*;?\s*;?\s*\)", source):
        finding(report, "error", "SCENE_UNBOUNDED_LOOP",
                "A potentially unbounded loop pattern was detected.",
                "Remove blocking loops; keep scene initialization finite and frame updates synchronous.")

    if not re.search(r"window\s*\.\s*setTime\s*=\s*(?:function|\([^)]*\)\s*=>)", source):
        finding(report, "warning", "SCENE_SET_TIME_SHAPE",
                "Could not statically identify a conventional setTime function assignment.",
                "Confirm the scene exports window.setTime(t) and test arbitrary frame seek order.")

    # A basic warning only: static code cannot prove visual variety.
    if len(source) < 500:
        finding(report, "warning", "SCENE_SOURCE_SHORT",
                "Scene source is unusually short; visual complexity cannot be inferred from this file.",
                "Inspect rendered frames rather than relying on source length.")


def _parse_rate(value: str) -> float | None:
    try:
        numerator, denominator = value.split("/", 1)
        denominator_value = float(denominator)
        return float(numerator) / denominator_value if denominator_value else None
    except (ValueError, AttributeError):
        return None


def audit_video(video: Path, expected_duration: float | None,
                report: list[dict[str, str]]) -> dict[str, Any] | None:
    ffprobe = shutil.which("ffprobe")
    if not video.is_file():
        finding(report, "warning", "VIDEO_NOT_PROVIDED",
                f"Rendered video not found: {video}",
                "Run the render and mix stages, then pass the final MP4 with --video.")
        return None
    if not ffprobe:
        finding(report, "warning", "FFPROBE_UNAVAILABLE",
                "ffprobe is unavailable; container, codec, duration and stream checks were skipped.",
                "Install FFmpeg/ffprobe in the audit environment.")
        return None

    cmd = [
        ffprobe, "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,r_frame_rate,codec_name",
        "-of", "json", str(video)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        finding(report, "error", "VIDEO_PROBE_FAILED",
                f"ffprobe could not inspect the video: {result.stderr.strip()[:300]}",
                "Check that the MP4 is complete and playable.")
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        finding(report, "error", "VIDEO_PROBE_INVALID", "ffprobe returned invalid JSON.")
        return None

    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    if not video_streams:
        finding(report, "error", "VIDEO_STREAM_MISSING", "No video stream was found.")
        return None
    stream = video_streams[0]
    try:
        duration = float(data.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        duration = None

    if duration is not None and expected_duration is not None:
        delta = abs(duration - expected_duration)
        if delta > max(0.75, expected_duration * 0.01):
            finding(report, "error", "VIDEO_DURATION_MISMATCH",
                    f"Video duration {duration:.2f}s differs from project duration {expected_duration:.2f}s.",
                    "Check timings.json, render --duration and the final mix -t value.")
    if not audio_streams:
        finding(report, "warning", "VIDEO_AUDIO_MISSING",
                "No audio stream was found. This may be a silent render rather than the final mixed video.",
                "If this is the final deliverable, run mix.py and audit the mixed MP4.")

    fps = _parse_rate(stream.get("r_frame_rate", ""))
    if fps is not None and not 20 <= fps <= 60:
        finding(report, "warning", "VIDEO_FRAME_RATE",
                f"Video frame rate is {fps:.3f} fps; expected educational-video range is typically 24–60 fps.")
    if stream.get("width", 0) < 640 or stream.get("height", 0) < 360:
        finding(report, "warning", "VIDEO_RESOLUTION",
                f"Video resolution is {stream.get('width')}x{stream.get('height')}; this is low for a 1080p target.")

    metrics = {
        "path": str(video),
        "duration_seconds": duration,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": fps,
        "video_codec": stream.get("codec_name"),
        "audio_present": bool(audio_streams),
    }
    visual = _sample_visual_diversity(video, report)
    if visual:
        metrics["visual_sample"] = visual
    return metrics


def _sample_visual_diversity(video: Path, report: list[dict[str, str]]) -> dict[str, Any] | None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        finding(report, "warning", "FFMPEG_UNAVAILABLE",
                "ffmpeg is unavailable; sampled-frame visual diversity check was skipped.")
        return None
    # Small grayscale samples are enough to flag identical/near-static output;
    # this is a screening heuristic, not semantic visual-quality recognition.
    command = [
        ffmpeg, "-v", "error", "-i", str(video),
        "-vf", "fps=1,scale=32:18:flags=area,format=gray",
        "-frames:v", "120", "-f", "rawvideo", "-"
    ]
    result = subprocess.run(command, capture_output=True)
    frame_size = 32 * 18
    raw = result.stdout
    count = len(raw) // frame_size
    if result.returncode or count < 2:
        finding(report, "warning", "VISUAL_SAMPLE_UNAVAILABLE",
                "Could not extract at least two one-second visual samples from the video.")
        return None

    frames = [raw[i * frame_size:(i + 1) * frame_size] for i in range(count)]
    hashes = [hashlib.sha1(frame).hexdigest() for frame in frames]
    exact_duplicates = sum(1 for a, b in zip(hashes, hashes[1:]) if a == b)
    differences = []
    for a, b in zip(frames, frames[1:]):
        differences.append(sum(abs(x - y) for x, y in zip(a, b)) / frame_size)
    mean_diff = sum(differences) / len(differences)
    duplicate_ratio = exact_duplicates / max(1, count - 1)
    if duplicate_ratio >= 0.60:
        finding(report, "warning", "VISUAL_REPETITION",
                f"{duplicate_ratio:.0%} of adjacent one-second samples are pixel-identical.",
                "Inspect the storyboard and sampled frames; the video may be holding or repeating the same visual.")
    elif mean_diff < 1.0:
        finding(report, "warning", "LOW_VISUAL_CHANGE",
                f"Average sampled-frame pixel change is very low ({mean_diff:.2f}/255).",
                "Check for static scenes, missing animation updates, or repeated short loops.")
    return {
        "sampled_frames": count,
        "adjacent_identical_ratio": round(duplicate_ratio, 3),
        "mean_adjacent_pixel_difference": round(mean_diff, 3),
        "method": "1 fps, 32x18 grayscale; heuristic only",
    }


def run_audit(root: Path, project_path: Path, timings_path: Path | None = None,
              scene_path: Path | None = None, video_path: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    project = _read_json(project_path)
    for error in validate_project(project):
        finding(findings, "error", "PROJECT_CONTRACT", error,
                "Fix the project brief before production.")
    audit_timeline(project, findings)

    if timings_path:
        if timings_path.is_file():
            timings = _read_json(timings_path)
            for error in validate_timings(timings):
                finding(findings, "error", "TIMINGS_CONTRACT", error,
                        "Regenerate or correct timings.json from the voice build.")
            if isinstance(timings.get("duration"), (int, float)):
                delta = abs(timings["duration"] - project.get("duration_seconds", 0))
                if delta > max(0.75, project.get("duration_seconds", 0) * 0.01):
                    finding(findings, "warning", "TIMINGS_PROJECT_DURATION",
                            f"Audio timing duration {timings['duration']:.2f}s differs from project duration.",
                            "Align the storyboard/project duration with the actual generated narration.")
        else:
            finding(findings, "warning", "TIMINGS_FILE_MISSING",
                    f"Timing file not found: {timings_path}",
                    "Generate voice.wav and timings.json before the final timing audit.")

    if scene_path:
        audit_scene_html(scene_path, findings)
    elif isinstance(project.get("render"), dict) and project["render"].get("scene_file"):
        candidate = _safe_path(root, project["render"]["scene_file"])
        if candidate is None:
            finding(findings, "error", "SCENE_PATH_UNSAFE",
                    "render.scene_file points outside the repository root.")
        else:
            audit_scene_html(candidate, findings)

    video_metrics = audit_video(video_path, project.get("duration_seconds"), findings) if video_path else None

    deductions = {"error": 15, "warning": 5, "info": 1}
    score = max(0, 100 - sum(deductions[item["severity"]] for item in findings))
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    status = "fail" if errors else ("review_required" if warnings else "pass")
    return {
        "quality_controller_version": "0.1.0",
        "project_id": project.get("project", {}).get("id", "unknown"),
        "status": status,
        "score": score,
        "summary": {"errors": errors, "warnings": warnings, "findings": len(findings)},
        "inputs": {
            "project": str(project_path),
            "timings": str(timings_path) if timings_path else None,
            "scene": str(scene_path) if scene_path else None,
            "video": str(video_path) if video_path else None,
        },
        "video": video_metrics,
        "findings": findings,
        "limitations": [
            "Static HTML checks cannot prove semantic relevance, readability, scientific accuracy or visual polish.",
            "Pixel-sample diversity is a coarse heuristic and cannot recognize meaningful scene changes.",
            "A human review of representative frames and the complete audio/video remains mandatory.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# FARACHI Quality Report",
        "",
        f"- Project: `{report['project_id']}`",
        f"- Status: **{report['status']}**",
        f"- Score: **{report['score']}/100** (heuristic)",
        f"- Errors: {report['summary']['errors']} | Warnings: {report['summary']['warnings']}",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No automated findings.")
    for item in report["findings"]:
        lines.append(f"- **{item['severity'].upper()} — {item['code']}**: {item['message']}")
        if item.get("recommendation"):
            lines.append(f"  - Recommendation: {item['recommendation']}")
    lines += ["", "## Limitations", ""]
    lines += [f"- {item}" for item in report["limitations"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FARACHI Quality Controller")
    parser.add_argument("project_json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--timings")
    parser.add_argument("--scene")
    parser.add_argument("--video")
    parser.add_argument("--json-out", default="build/quality-report.json")
    parser.add_argument("--md-out", default="build/quality-report.md")
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).resolve()
        project_path = _safe_path(root, args.project_json)
        if project_path is None:
            raise CoreError("project_json must be inside --root")
        timings_path = _safe_path(root, args.timings) if args.timings else None
        scene_path = _safe_path(root, args.scene) if args.scene else None
        video_path = _safe_path(root, args.video) if args.video else None
        if args.timings and timings_path is None:
            raise CoreError("--timings must be inside --root")
        if args.scene and scene_path is None:
            raise CoreError("--scene must be inside --root")
        if args.video and video_path is None:
            raise CoreError("--video must be inside --root")

        report = run_audit(root, project_path, timings_path, scene_path, video_path)
        json_out = _safe_path(root, args.json_out)
        md_out = _safe_path(root, args.md_out)
        if json_out is None or md_out is None:
            raise CoreError("Report output paths must be inside --root")
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_markdown(report, md_out)
        print(f"Quality status: {report['status']} | score: {report['score']}/100")
        print(f"Errors: {report['summary']['errors']} | Warnings: {report['summary']['warnings']}")
        print(f"JSON report: {json_out}")
        print(f"Markdown report: {md_out}")
        return 1 if report["status"] == "fail" else 0
    except (CoreError, OSError, json.JSONDecodeError) as exc:
        print(f"QUALITY CONTROLLER ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
