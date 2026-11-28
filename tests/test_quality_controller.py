import tempfile
import unittest
from pathlib import Path

from farachi_core.quality_controller import (
    audit_scene_html,
    audit_timeline,
    run_audit,
)


class QualityControllerTests(unittest.TestCase):
    def test_timeline_gap_is_reported(self):
        report = []
        project = {
            "duration_seconds": 10,
            "scenes": [
                {"id": "a", "start": 0, "end": 3},
                {"id": "b", "start": 4, "end": 10},
            ],
        }
        audit_timeline(project, report)
        self.assertTrue(any(x["code"] == "TIMELINE_GAP" for x in report))

    def test_timeline_overlap_is_error(self):
        report = []
        project = {
            "duration_seconds": 10,
            "scenes": [
                {"id": "a", "start": 0, "end": 5},
                {"id": "b", "start": 4, "end": 10},
            ],
        }
        audit_timeline(project, report)
        self.assertTrue(any(
            x["code"] == "TIMELINE_OVERLAP" and x["severity"] == "error"
            for x in report
        ))

    def test_nested_timeline_overlap_is_detected(self):
        report = []
        project = {
            "duration_seconds": 10,
            "scenes": [
                {"id": "long", "start": 0, "end": 8},
                {"id": "nested", "start": 2, "end": 3},
                {"id": "after", "start": 8, "end": 10},
            ],
        }
        audit_timeline(project, report)
        self.assertTrue(any(x["code"] == "TIMELINE_OVERLAP" for x in report))

    def test_scene_contract_and_nondeterminism_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            scene = Path(temp) / "scene.html"
            scene.write_text(
                "<html><script>window.ready=true; "
                "window.setTime=(t)=>{}; setInterval(()=>{},100);</script></html>",
                encoding="utf-8",
            )
            report = []
            audit_scene_html(scene, report)
            codes = {x["code"] for x in report}
            self.assertIn("SCENE_NONDETERMINISM", codes)
            self.assertNotIn("SCENE_READY_CONTRACT", codes)
            self.assertNotIn("SCENE_SETTIME_CONTRACT", codes)

    def test_unbounded_while_loop_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            scene = Path(temp) / "scene.html"
            scene.write_text(
                "<html><script>window.ready=true; window.setTime=(t)=>{}; while(true) {}</script></html>",
                encoding="utf-8",
            )
            report = []
            audit_scene_html(scene, report)
            self.assertIn("SCENE_UNBOUNDED_LOOP", {x["code"] for x in report})

    def test_missing_scene_contract_is_error(self):
        with tempfile.TemporaryDirectory() as temp:
            scene = Path(temp) / "scene.html"
            scene.write_text("<html><body>static</body></html>", encoding="utf-8")
            report = []
            audit_scene_html(scene, report)
            self.assertIn("SCENE_READY_CONTRACT", {x["code"] for x in report})
            self.assertIn("SCENE_SETTIME_CONTRACT", {x["code"] for x in report})

    def test_full_report_marks_unrendered_example_for_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project_file = root / "project.json"
            project_file.write_text(
                """{
                  "schema_version": "1.0",
                  "project": {"id": "qc-demo", "title": "QC demo"},
                  "duration_seconds": 10,
                  "scenes": [
                    {"id": "one", "start": 0, "end": 5, "visual": "First scene"},
                    {"id": "two", "start": 5, "end": 10, "visual": "Second scene"}
                  ]
                }""",
                encoding="utf-8",
            )
            report = run_audit(root, project_file)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
