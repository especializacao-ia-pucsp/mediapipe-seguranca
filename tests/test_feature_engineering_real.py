from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mediapipe_seguranca.build_processed_base import build_processed_base  # noqa: E402
from mediapipe_seguranca.feature_engineering_real import (  # noqa: E402
    FRAME_FEATURES_SCHEMA,
    WINDOW_FEATURES_SCHEMA,
    aggregate_window_features_real,
    build_frame_features,
    compute_quality_report,
)
from mediapipe_seguranca.mediapipe_extract import FRAME_SCHEMA  # noqa: E402


def _make_raw_frames(video_id: str, n: int, motion_scale: float = 1.0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "video_id": [video_id] * n,
            "frame_index": list(range(n)),
            "num_people_detected": [(i % 6) for i in range(n)],
            "mean_pose_visibility": [0.5 + (i % 3) * 0.1 for i in range(n)],
            "bbox_area_total": [0.05 * (i % 6) for i in range(n)],
            "mean_bbox_area": [0.02 * (i % 4) for i in range(n)],
            "motion_proxy": [motion_scale * (i % 5) for i in range(n)],
            "detector_fallback_used": [(i % 7 == 0) for i in range(n)],
        }
    )


class FrameFeaturesTests(unittest.TestCase):
    def test_frame_features_schema(self) -> None:
        df = _make_raw_frames("video_a", 10)
        out = build_frame_features(df, window_size=5)
        self.assertEqual(list(out.columns), FRAME_FEATURES_SCHEMA)
        self.assertEqual(out["window_id"].dtype.kind, "i")
        self.assertEqual(out["num_people_detected"].dtype.kind, "i")
        self.assertEqual(out["is_dense_scene"].dtype, bool)
        self.assertEqual(out["is_empty_scene"].dtype, bool)
        # all input columns from FRAME_SCHEMA preserved
        for col in FRAME_SCHEMA:
            self.assertIn(col, out.columns)

    def test_motion_proxy_norm_per_video(self) -> None:
        a = _make_raw_frames("vid_a", 8, motion_scale=10.0)
        b = _make_raw_frames("vid_b", 8, motion_scale=0.1)
        df = pd.concat([a, b], ignore_index=True)
        out = build_frame_features(df, window_size=4)
        for video_id in ("vid_a", "vid_b"):
            sub = out[out["video_id"] == video_id]
            self.assertGreaterEqual(sub["motion_proxy_norm"].min(), 0.0)
            self.assertLessEqual(sub["motion_proxy_norm"].max(), 1.0 + 1e-9)
            self.assertAlmostEqual(sub["motion_proxy_norm"].max(), 1.0, places=6)


class WindowAggregationTests(unittest.TestCase):
    def test_window_aggregation_keys_and_counts(self) -> None:
        df = _make_raw_frames("vid_x", 30)
        frame_features = build_frame_features(df, window_size=15)
        windows = aggregate_window_features_real(frame_features)
        self.assertEqual(len(windows), 2)
        self.assertEqual(set(windows["window_id"].tolist()), {0, 1})
        self.assertTrue((windows["frames_in_window"] == 15).all())
        self.assertTrue((windows["people_peak"] >= 0).all())
        self.assertTrue((windows["motion_delta"] >= 0).all())

    def test_window_features_schema(self) -> None:
        df = _make_raw_frames("vid_y", 16)
        frame_features = build_frame_features(df, window_size=8)
        windows = aggregate_window_features_real(frame_features)
        self.assertEqual(list(windows.columns), WINDOW_FEATURES_SCHEMA)


class QualityReportTests(unittest.TestCase):
    def test_quality_report_structure(self) -> None:
        df = _make_raw_frames("vid_q", 20)
        # inject some NaNs
        df.loc[2, "mean_pose_visibility"] = np.nan
        frames = build_frame_features(df, window_size=10)
        windows = aggregate_window_features_real(frames)
        report = compute_quality_report(frames, windows)
        for key in (
            "total_frames",
            "total_videos",
            "total_windows",
            "missing_per_column",
            "value_ranges",
            "outlier_flags",
            "frames_without_detection",
            "frames_with_fallback",
            "pipeline_version",
        ):
            self.assertIn(key, report)
        # JSON serializable
        json.dumps(report)


class BuildProcessedBaseTests(unittest.TestCase):
    def test_build_processed_base_with_tmp_path(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            interim = tmp_path / "interim"
            training = interim / "training"
            training.mkdir(parents=True)
            _make_raw_frames("video_001", 30).to_parquet(training / "video_001.parquet", index=False)
            _make_raw_frames("video_002", 16, motion_scale=2.0).to_parquet(training / "video_002.parquet", index=False)
            output = tmp_path / "processed"

            summary = build_processed_base(
                interim_dir=interim,
                output_dir=output,
                window_size=15,
                splits=("training",),
            )

            for fname in (
                "frame_features_real.parquet",
                "frame_features_real.csv",
                "window_features_real.parquet",
                "window_features_real.csv",
                "data_quality_report.json",
            ):
                self.assertTrue((output / fname).exists(), fname)

            for key in ("frames", "windows", "videos", "splits", "output_dir", "quality_report_path"):
                self.assertIn(key, summary)
            self.assertEqual(summary["videos"], 2)
            self.assertEqual(summary["frames"], 46)


if __name__ == "__main__":
    unittest.main()
