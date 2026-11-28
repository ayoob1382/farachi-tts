#!/usr/bin/env python3
"""FARACHI skill registry, project validation, and deterministic orchestration.

This module plans work; it does not execute LLM skills or render video.
The existing render.js remains the rendering engine.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PRODUCTION_ORDER = [
    "farachi-animation-director",
    "storyboarding",
    "motion-design",
    "composition",
    "2d-animation",
    "kinetic-typography",
    "animated-charts",
    "infographics",
    "visual-effects",
    "timing-easing",
    "transitions",
    "video-rendering",
]

ROUTES = {
    "character": ["2d-animation"],
    "objects": ["2d-animation"],
    "text": ["kinetic-typography"],
    "typography": ["kinetic-typography"],
    "data": ["animated-charts"],
    "chart": ["animated-charts"],
    "process": ["infographics"],
    "diagram": ["infographics"],
    "effects": ["visual-effects"],
    "vfx": ["visual-effects"],
}


class CoreError(ValueError):
    """Raised when a registry or project violates the FARACHI contract."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoreError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CoreError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"Expected a JSON object in {path}")
    return value


class SkillRegistry:
    """Loads registry.json and validates each registered skill manifest."""

    def __init__(self, repo_root: str | Path, registry_path: str = "skills/registry.json"):
        self.root = Path(repo_root).resolve()
        self.registry_path = self.root / registry_path
        self.data = _read_json(self.registry_path)
        entries = self.data.get("skills")
        if not isinstance(entries, list):
            raise CoreError("skills/registry.json must contain a 'skills' array")

        self.skills: dict[str, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise CoreError("Every registry entry must be an object")
            skill_id = entry.get("id")
            skill_path = entry.get("path")
            manifest_path = entry.get("manifest")
            if not all(isinstance(x, str) and x for x in (skill_id, skill_path, manifest_path)):
                raise CoreError(f"Registry entry is missing id/path/manifest: {entry!r}")
            if skill_id in self.skills:
                raise CoreError(f"Duplicate skill id: {skill_id}")

            guide = self.root / skill_path
            manifest_file = self.root / manifest_path
            if not guide.is_file():
                raise CoreError(f"Skill guide does not exist: {skill_path}")
            manifest = _read_json(manifest_file)
            if manifest.get("id") != skill_id:
                raise CoreError(
                    f"Manifest id mismatch for {skill_id}: {manifest.get('id')!r}"
                )
            if manifest.get("entrypoint", "SKILL.md") != guide.name:
                raise CoreError(f"Unexpected entrypoint for {skill_id}: {manifest_path}")
            self.skills[skill_id] = {
                **entry,
                "name": manifest.get("name", entry.get("name", skill_id)),
                "description": manifest.get("description", ""),
                "tags": manifest.get("tags", []),
                "depends_on": manifest.get("depends_on", []),
                "manifest_path": manifest_path,
                "guide_path": skill_path,
            }

        if not self.skills:
            raise CoreError("No skills are registered")

    def get(self, skill_id: str) -> dict[str, Any]:
        if skill_id not in self.skills:
            raise CoreError(f"Unknown skill id: {skill_id}")
        return self.skills[skill_id]

    def ordered(self, requested: list[str] | None = None) -> list[str]:
        """Resolve dependencies and return a stable topological production order."""
        requested = requested or list(PRODUCTION_ORDER)
        selected: set[str] = set()
        visiting: set[str] = set()
        ordered: list[str] = []

        def include(skill_id: str) -> None:
            if skill_id in visiting:
                raise CoreError(f"Circular skill dependency detected at: {skill_id}")
            if skill_id in selected:
                return
            skill = self.get(skill_id)
            visiting.add(skill_id)
            deps = skill.get("depends_on", [])
            if not isinstance(deps, list):
                raise CoreError(f"depends_on must be an array for {skill_id}")
            for dep in deps:
                if not isinstance(dep, str):
                    raise CoreError(f"Invalid dependency in {skill_id}: {dep!r}")
                include(dep)
            visiting.remove(skill_id)
            selected.add(skill_id)
            ordered.append(skill_id)

        order_index = {name: i for i, name in enumerate(PRODUCTION_ORDER)}
        roots = sorted(dict.fromkeys(requested), key=lambda item: (order_index.get(item, len(order_index)), item))
        for skill_id in roots:
            include(skill_id)
        return ordered


def select_skills(task: str, explicit: list[str] | None = None) -> list[str]:
    """Choose relevant scene-specific skills from plain task keywords."""
    text = (task or "").lower()
    chosen = list(explicit or [])
    for keyword, skill_ids in ROUTES.items():
        if re.search(rf"\b{re.escape(keyword)}s?\b", text):
            chosen.extend(skill_ids)
    # Stable de-duplication.
    return list(dict.fromkeys(chosen))


def build_execution_plan(
    project: dict[str, Any], registry: SkillRegistry
) -> dict[str, Any]:
    """Build a reproducible plan. It describes skill order; it does not run models."""
    project_meta = project.get("project", {})
    task = " ".join(
        str(project_meta.get(key, ""))
        for key in ("title", "description", "visual_focus")
    )
    requested = project.get("selected_skills", [])
    if not isinstance(requested, list):
        raise CoreError("selected_skills must be an array")
    scene_requested = [
        skill_id
        for scene in project.get("scenes", [])
        if isinstance(scene, dict)
        for skill_id in scene.get("skill_ids", [])
    ]
    routed = select_skills(task, list(dict.fromkeys(requested + scene_requested)))
    # Base production passes are always included. Scene-specific skills are added
    # only when requested or detected from the brief.
    base = [
        "farachi-animation-director",
        "storyboarding",
        "motion-design",
        "composition",
        "timing-easing",
        "transitions",
        "video-rendering",
    ]
    ordered = registry.ordered(list(dict.fromkeys(base + routed)))
    return {
        "core_version": "0.1.0",
        "project_id": project_meta.get("id", "unnamed-project"),
        "plan_status": "planned_not_executed",
        "renderer": {
            "engine": "render.js",
            "scene_contract": ["window.ready === true", "window.setTime(t)"],
            "timings_file": "timings.json",
        },
        "steps": [
            {
                "order": index + 1,
                "skill_id": skill_id,
                "name": registry.get(skill_id)["name"],
                "guide": registry.get(skill_id)["guide_path"],
                "purpose": registry.get(skill_id)["description"],
            }
            for index, skill_id in enumerate(ordered)
        ],
    }


def validate_timings(data: dict[str, Any]) -> list[str]:
    """Validate the timings.json contract produced by build_audio.py."""
    errors: list[str] = []
    duration = data.get("duration")
    sentences = data.get("sentences")
    if not isinstance(duration, (int, float)) or duration <= 0:
        errors.append("duration must be a positive number")
    if not isinstance(sentences, list) or not sentences:
        errors.append("sentences must be a non-empty array")
        return errors
    previous_end = 0.0
    for index, item in enumerate(sentences):
        if not isinstance(item, dict):
            errors.append(f"sentences[{index}] must be an object")
            continue
        start, end, text = item.get("start"), item.get("end"), item.get("text")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            errors.append(f"sentences[{index}] start/end must be numbers")
            continue
        if start < 0 or end <= start:
            errors.append(f"sentences[{index}] has an invalid time range")
        if start < previous_end - 0.001:
            errors.append(f"sentences[{index}] overlaps the previous sentence")
        if isinstance(duration, (int, float)) and end > duration + 0.05:
            errors.append(f"sentences[{index}] ends after total duration")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"sentences[{index}] text must be a non-empty string")
        previous_end = max(previous_end, end)
    return errors


def validate_project(project: dict[str, Any]) -> list[str]:
    """Validate the shared project brief/timeline contract."""
    errors: list[str] = []
    if project.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    meta = project.get("project")
    if not isinstance(meta, dict):
        errors.append("project must be an object")
        meta = {}
    if not isinstance(meta.get("id"), str) or not meta.get("id", "").strip():
        errors.append("project.id is required")
    if not isinstance(meta.get("title"), str) or not meta.get("title", "").strip():
        errors.append("project.title is required")

    duration = project.get("duration_seconds")
    if not isinstance(duration, (int, float)) or duration <= 0:
        errors.append("duration_seconds must be a positive number")

    scenes = project.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty array")
        return errors

    seen: set[str] = set()
    for index, scene in enumerate(scenes):
        prefix = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            errors.append(f"{prefix}.id is required")
        elif scene_id in seen:
            errors.append(f"duplicate scene id: {scene_id}")
        else:
            seen.add(scene_id)
        start, end = scene.get("start"), scene.get("end")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            errors.append(f"{prefix}.start and end must be numbers")
            continue
        if start < 0 or end <= start:
            errors.append(f"{prefix} has an invalid time range")
        if isinstance(duration, (int, float)) and end > duration + 0.001:
            errors.append(f"{prefix} ends after duration_seconds")
        if not isinstance(scene.get("visual"), str) or not scene["visual"].strip():
            errors.append(f"{prefix}.visual is required")
        skill_ids = scene.get("skill_ids", [])
        if not isinstance(skill_ids, list) or not all(isinstance(x, str) for x in skill_ids):
            errors.append(f"{prefix}.skill_ids must be an array of strings")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FARACHI Core project and skill manager")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("list-skills",):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".")

    for name in ("plan", "validate-project"):
        p = sub.add_parser(name)
        p.add_argument("project_json")
        p.add_argument("--root", default=".")
        if name == "plan":
            p.add_argument("--out", default="build/execution-plan.json")

    p = sub.add_parser("validate-timings")
    p.add_argument("timings_json")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-timings":
            errors = validate_timings(_read_json(Path(args.timings_json)))
            if errors:
                print("\n".join(f"ERROR: {item}" for item in errors))
                return 1
            print("timings.json: valid")
            return 0

        if args.command == "list-skills":
            registry = SkillRegistry(args.root)
            for item in registry.skills.values():
                print(f"{item['id']}\t{item['name']}\t{item['status']}")
            return 0

        project = _read_json(Path(args.project_json))
        errors = validate_project(project)
        if errors:
            print("\n".join(f"ERROR: {item}" for item in errors))
            return 1
        if args.command == "validate-project":
            print("project: valid")
            return 0

        registry = SkillRegistry(args.root)
        plan = build_execution_plan(project, registry)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Execution plan written: {output}")
        print("Status: planned_not_executed (no skill/model execution was attempted)")
        return 0
    except CoreError as exc:
        print(f"FARACHI CORE ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
