from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mediapipe_seguranca import mediapipe_extract  # noqa: E402
from mediapipe_seguranca.mediapipe_extract import FRAME_SCHEMA, extract_video  # noqa: E402

EXPECTED_SCHEMA = [
    "video_id",
    "frame_index",
    "num_people_detected",
    "mean_pose_visibility",
    "bbox_area_total",
    "mean_bbox_area",
    "motion_proxy",
    "detector_fallback_used",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _DummyExtractor:
    """Stand-in for :class:`MediaPipeExtractor` used in the tests."""

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        self.calls = 0

    def extract_frame(self, image_bgr: np.ndarray, prev_gray: np.ndarray | None = None) -> dict[str, Any]:
        self.calls += 1
        return {
            "video_id": "",
            "frame_index": 0,
            "num_people_detected": 2,
            "mean_pose_visibility": 0.85,
            "bbox_area_total": 120.0,
            "mean_bbox_area": 60.0,
            "motion_proxy": 0.0 if prev_gray is None else 1.5,
            "detector_fallback_used": False,
        }

    def close(self) -> None:
        return None

    def __enter__(self) -> "_DummyExtractor":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()


def _synthetic_frames(n: int) -> list[tuple[int, np.ndarray]]:
    rng = np.random.default_rng(seed=42)
    return [(i, rng.integers(0, 255, size=(8, 8, 3), dtype=np.uint8)) for i in range(n)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_frame_schema_constant() -> None:
    assert FRAME_SCHEMA == EXPECTED_SCHEMA
    assert len(FRAME_SCHEMA) == 8


def test_extract_video_with_mock_extractor() -> None:
    extractor = _DummyExtractor()
    frames = _synthetic_frames(20)
    stride = 5

    df = extract_video(extractor, frames, video_id="vid_x", frame_stride=stride)

    expected_rows = math.ceil(20 / stride)
    assert len(df) == expected_rows
    assert list(df.columns) == FRAME_SCHEMA
    assert df["video_id"].unique().tolist() == ["vid_x"]
    assert df["frame_index"].tolist() == [0, 5, 10, 15]
    assert df["motion_proxy"].iloc[0] == 0.0
    # Subsequent frames receive prev_gray, our dummy returns 1.5 for those.
    assert (df["motion_proxy"].iloc[1:] == 1.5).all()
    assert df.dtypes["frame_index"] == np.int64
    assert df.dtypes["num_people_detected"] == np.int64
    assert df.dtypes["bbox_area_total"] == np.float64
    assert df.dtypes["mean_pose_visibility"] == np.float64
    assert df.dtypes["motion_proxy"] == np.float64
    assert df.dtypes["detector_fallback_used"] == np.bool_


def test_extract_video_empty_returns_typed_dataframe() -> None:
    extractor = _DummyExtractor()
    df = extract_video(extractor, iter([]), video_id="vid_empty")
    assert df.empty
    assert list(df.columns) == FRAME_SCHEMA


def test_run_extraction_idempotent(tmp_path: Path) -> None:
    from mediapipe_seguranca import extract_runner

    # Build a fake "training" set with two video directories containing JPGs.
    train_root = tmp_path / "training" / "frames"
    video_dirs: list[Path] = []
    for vid in ("01_001", "01_002"):
        vdir = train_root / vid
        vdir.mkdir(parents=True, exist_ok=True)
        for idx in range(6):
            # Tiny placeholder JPGs are fine — cv2.imread is also patched out below.
            (vdir / f"{idx:03d}.jpg").write_bytes(b"\x00")
        video_dirs.append(vdir)

    output_dir = tmp_path / "out"

    fake_image = np.zeros((4, 4, 3), dtype=np.uint8)

    def fake_iter_frames(video_dir: Path):
        for i in range(6):
            yield i, video_dir / f"{i:03d}.jpg"

    def fake_imread(_path: str, *_args: Any, **_kwargs: Any) -> np.ndarray:
        return fake_image

    with patch.object(extract_runner.shanghaitech_loader, "get_train_videos", return_value=video_dirs), patch.object(
        extract_runner.shanghaitech_loader, "get_test_videos_with_gt", return_value=[]
    ), patch.object(extract_runner.shanghaitech_loader, "iter_frames", side_effect=fake_iter_frames), patch.object(
        extract_runner, "MediaPipeExtractor", _DummyExtractor
    ), patch.object(
        extract_runner.cv2, "imread", side_effect=fake_imread
    ):

        manifest_first = extract_runner.run_extraction(
            split="training",
            frame_stride=2,
            output_dir=output_dir,
            model_dir=tmp_path / "models",
        )
        first_mtimes = {p: p.stat().st_mtime_ns for p in (output_dir / "training").glob("*.parquet")}

        manifest_second = extract_runner.run_extraction(
            split="training",
            frame_stride=2,
            output_dir=output_dir,
            model_dir=tmp_path / "models",
        )
        second_mtimes = {p: p.stat().st_mtime_ns for p in (output_dir / "training").glob("*.parquet")}

    assert len(manifest_first) == 2
    # Manifesto reflete os 2 vídeos após segunda execução também (sem duplicar).
    assert len(manifest_second) == 2
    assert first_mtimes == second_mtimes  # idempotente: arquivos não foram reescritos.


@pytest.mark.slow
def test_real_extractor_smoke() -> None:
    """Optional smoke test that hits real MediaPipe runtime."""
    pose_model = ROOT / "models" / "mediapipe" / "pose_landmarker_lite.task"
    if not pose_model.exists():
        pytest.skip("Modelo pose_landmarker_lite.task ausente; rode scripts/download_mediapipe_models.py")

    extractor = mediapipe_extract.MediaPipeExtractor(model_dir=pose_model.parent)
    try:
        frame = np.full((240, 320, 3), 128, dtype=np.uint8)
        record = extractor.extract_frame(frame)
    finally:
        extractor.close()

    for key in FRAME_SCHEMA:
        if key in ("video_id", "frame_index"):
            continue
        assert key in record
