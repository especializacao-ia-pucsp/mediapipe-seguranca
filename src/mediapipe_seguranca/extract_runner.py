"""Batch runner for MediaPipe extraction over the ShanghaiTech dataset.

Iterates videos returned by :mod:`shanghaitech_loader`, runs
:class:`MediaPipeExtractor` over each frame, persists per-video parquet files
and updates a manifest describing what has been processed.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable, Iterator

import cv2
import numpy as np
import pandas as pd

from . import shanghaitech_loader
from .config import get_project_paths
from .mediapipe_extract import MediaPipeExtractor, extract_video

try:  # tqdm is optional during tests
    from tqdm import tqdm
except Exception:  # pragma: no cover - fallback when tqdm unavailable

    def tqdm(iterable: Iterable, **_kwargs: object) -> Iterable:  # type: ignore[misc]
        return iterable


def _mediapipe_version() -> str:
    try:
        import mediapipe as mp

        return getattr(mp, "__version__", "unknown")
    except Exception:
        return "unknown"


MANIFEST_NAME = "_manifest.parquet"
MANIFEST_SCHEMA: list[str] = [
    "video_id",
    "split",
    "num_frames_in",
    "num_frames_processed",
    "frame_stride",
    "mean_people",
    "has_gt_mask",
    "processing_seconds",
    "mediapipe_version",
]


def _iter_video_frames(video_dir: Path) -> Iterator[tuple[int, np.ndarray]]:
    """Yield ``(frame_index, BGR ndarray)`` pairs for every JPG in ``video_dir``."""
    for idx, frame_path in shanghaitech_loader.iter_frames(video_dir):
        image = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
        if image is None:
            continue
        yield idx, image


def _list_videos(split: str) -> list[tuple[Path, str, bool]]:
    """Return a list of ``(video_dir, split, has_gt_mask)`` for the requested split."""
    videos: list[tuple[Path, str, bool]] = []
    if split in ("training", "both"):
        for video_dir in shanghaitech_loader.get_train_videos():
            videos.append((video_dir, "training", False))
    if split in ("testing", "both"):
        for video_dir, _mask_path in shanghaitech_loader.get_test_videos_with_gt():
            videos.append((video_dir, "testing", True))
    return videos


def _merge_manifest(existing: pd.DataFrame | None, new_rows: list[dict]) -> pd.DataFrame:
    new_df = pd.DataFrame(new_rows, columns=MANIFEST_SCHEMA)
    if existing is None or existing.empty:
        return new_df
    merged = pd.concat([existing, new_df], ignore_index=True)
    merged = merged.drop_duplicates(subset=["video_id", "split"], keep="last").reset_index(drop=True)
    return merged


def run_extraction(
    split: str = "training",
    frame_stride: int = 5,
    limit_videos: int | None = None,
    output_dir: Path | None = None,
    model_dir: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Run MediaPipe extraction over all videos of ``split``.

    Parameters
    ----------
    split:
        ``"training"``, ``"testing"`` or ``"both"``.
    frame_stride:
        Process one frame every ``frame_stride`` frames.
    limit_videos:
        Optional cap on the number of videos processed.
    output_dir:
        Destination for parquet files; defaults to
        ``data/interim/mediapipe_frames/``.
    model_dir:
        Directory containing ``pose_landmarker_lite.task`` and (optionally)
        ``efficientdet_lite0.tflite``. Defaults to ``models/mediapipe/``.
    force:
        Reprocess videos that already have parquet output.
    """
    if split not in {"training", "testing", "both"}:
        raise ValueError(f"split inválido: {split!r}")

    paths = get_project_paths()
    output_dir = output_dir or paths.interim_mediapipe_frames
    model_dir = model_dir or paths.models_mediapipe
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = _list_videos(split)
    if limit_videos is not None:
        videos = videos[:limit_videos]

    manifest_path = output_dir / MANIFEST_NAME
    existing_manifest: pd.DataFrame | None = None
    if manifest_path.exists():
        try:
            existing_manifest = pd.read_parquet(manifest_path)
        except Exception:
            existing_manifest = None

    new_rows: list[dict] = []

    if not videos:
        # Nothing to do — return existing manifest (or empty one).
        if existing_manifest is not None:
            return existing_manifest
        return pd.DataFrame(columns=MANIFEST_SCHEMA)

    with MediaPipeExtractor(model_dir=model_dir) as extractor:
        for video_dir, video_split, has_gt_mask in tqdm(videos, desc=f"extract:{split}"):
            video_id = video_dir.name
            split_dir = output_dir / video_split
            split_dir.mkdir(parents=True, exist_ok=True)
            target_parquet = split_dir / f"{video_id}.parquet"

            if target_parquet.exists() and not force:
                continue

            num_frames_in = sum(1 for _ in shanghaitech_loader.iter_frames(video_dir))
            t0 = time.perf_counter()
            df = extract_video(
                extractor,
                _iter_video_frames(video_dir),
                video_id=video_id,
                frame_stride=frame_stride,
            )
            processing_seconds = time.perf_counter() - t0

            df.to_parquet(target_parquet, index=False)

            mean_people = float(df["num_people_detected"].mean()) if not df.empty else 0.0
            new_rows.append(
                {
                    "video_id": video_id,
                    "split": video_split,
                    "num_frames_in": int(num_frames_in),
                    "num_frames_processed": int(len(df)),
                    "frame_stride": int(frame_stride),
                    "mean_people": mean_people,
                    "has_gt_mask": bool(has_gt_mask),
                    "processing_seconds": float(processing_seconds),
                    "mediapipe_version": _mediapipe_version(),
                }
            )

    manifest = _merge_manifest(existing_manifest, new_rows)
    if not manifest.empty:
        manifest.to_parquet(manifest_path, index=False)
    return manifest
