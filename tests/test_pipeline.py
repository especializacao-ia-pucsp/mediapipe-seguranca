from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mediapipe_seguranca import pipeline as pipeline_mod  # noqa: E402
from mediapipe_seguranca.config import ProjectPaths  # noqa: E402
from mediapipe_seguranca.pipeline import run_demo_pipeline, run_pipeline  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_demo_pipeline_creates_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "demo.csv"
            result = run_demo_pipeline(output_path=output_path)

            self.assertTrue(output_path.exists())
            self.assertGreater(result["rows"], 0)
            self.assertIn("normal", result["labels"])
            self.assertIn("evento_risco", result["labels"])

    def test_pipeline_processed_mode_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            interim = tmp_path / "interim_mp"
            training = interim / "training"
            training.mkdir(parents=True)
            n = 20
            df = pd.DataFrame(
                {
                    "video_id": ["v_smoke"] * n,
                    "frame_index": list(range(n)),
                    "num_people_detected": [(i % 5) for i in range(n)],
                    "mean_pose_visibility": [0.6 for _ in range(n)],
                    "bbox_area_total": [0.04 * (i % 4) for i in range(n)],
                    "mean_bbox_area": [0.01 * (i % 3) for i in range(n)],
                    "motion_proxy": [float(i % 4) for i in range(n)],
                    "detector_fallback_used": [False] * n,
                }
            )
            df.to_parquet(training / "v_smoke.parquet", index=False)

            processed = tmp_path / "processed"
            fake_paths = ProjectPaths(
                root=tmp_path,
                data_raw=tmp_path / "raw",
                data_interim=tmp_path / "interim",
                data_processed=processed,
                data_labels=tmp_path / "labels",
                reports=tmp_path / "reports",
                models_mediapipe=tmp_path / "models",
                interim_mediapipe_frames=interim,
            )

            original = pipeline_mod.get_project_paths
            pipeline_mod.get_project_paths = lambda root=None: fake_paths  # type: ignore[assignment]
            try:
                result = run_pipeline(mode="processed", split="training")
            finally:
                pipeline_mod.get_project_paths = original  # type: ignore[assignment]

            self.assertGreater(result["frames"], 0)
            self.assertGreater(result["windows"], 0)
            self.assertTrue((processed / "frame_features_real.parquet").exists())
            self.assertTrue((processed / "window_features_real.parquet").exists())
            self.assertTrue((processed / "data_quality_report.json").exists())


if __name__ == "__main__":
    unittest.main()
