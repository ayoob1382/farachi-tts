import json
import tempfile
import unittest
from pathlib import Path

from farachi_core.skill_manager import (
    CoreError,
    SkillRegistry,
    build_execution_plan,
    validate_project,
    validate_timings,
)


class CoreContractTests(unittest.TestCase):
    def test_timings_contract_accepts_build_audio_shape(self):
        data = {
            "duration": 3.0,
            "title": "sample",
            "sentences": [
                {"start": 0.6, "end": 1.4, "text": "سلام"},
                {"start": 1.85, "end": 2.5, "text": "دنیا"},
            ],
        }
        self.assertEqual(validate_timings(data), [])

    def test_timings_contract_rejects_overlap(self):
        data = {
            "duration": 3.0,
            "sentences": [
                {"start": 0.6, "end": 1.8, "text": "الف"},
                {"start": 1.7, "end": 2.5, "text": "ب"},
            ],
        }
        self.assertTrue(any("overlaps" in item for item in validate_timings(data)))

    def test_project_contract_accepts_minimal_project(self):
        project = {
            "schema_version": "1.0",
            "project": {"id": "demo", "title": "Demo"},
            "duration_seconds": 10,
            "scenes": [
                {"id": "scene-01", "start": 0, "end": 10, "visual": "A unique visual"},
            ],
        }
        self.assertEqual(validate_project(project), [])

    def test_project_rejects_duplicate_scene_ids(self):
        project = {
            "schema_version": "1.0",
            "project": {"id": "demo", "title": "Demo"},
            "duration_seconds": 10,
            "scenes": [
                {"id": "same", "start": 0, "end": 4, "visual": "One"},
                {"id": "same", "start": 4, "end": 10, "visual": "Two"},
            ],
        }
        self.assertTrue(any("duplicate scene id" in item for item in validate_project(project)))

    def test_registry_loads_and_builds_stable_plan(self):
        root = Path(__file__).resolve().parents[1]
        registry = SkillRegistry(root)
        project = {
            "schema_version": "1.0",
            "project": {"id": "demo", "title": "Demo", "visual_focus": "Persian typography and charts"},
            "duration_seconds": 10,
            "scenes": [{"id": "s1", "start": 0, "end": 10, "visual": "Animated chart"}],
        }
        plan = build_execution_plan(project, registry)
        ids = [step["skill_id"] for step in plan["steps"]]
        self.assertEqual(ids[0], "storyboarding")
        self.assertIn("kinetic-typography", ids)
        self.assertIn("animated-charts", ids)
        self.assertEqual(plan["plan_status"], "planned_not_executed")

    def test_registry_rejects_unknown_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "skills/demo").mkdir(parents=True)
            (root / "skills/registry.json").write_text(json.dumps({
                "skills": [{
                    "id": "demo",
                    "path": "skills/demo/SKILL.md",
                    "manifest": "skills/demo/manifest.json",
                    "status": "draft"
                }]
            }), encoding="utf-8")
            (root / "skills/demo/SKILL.md").write_text("# Demo", encoding="utf-8")
            (root / "skills/demo/manifest.json").write_text(json.dumps({
                "id": "demo",
                "entrypoint": "SKILL.md",
                "depends_on": ["missing"]
            }), encoding="utf-8")
            registry = SkillRegistry(root)
            with self.assertRaises(CoreError):
                registry.ordered(["demo"])


if __name__ == "__main__":
    unittest.main()
