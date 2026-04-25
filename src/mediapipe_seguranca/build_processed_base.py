"""Build the processed analytical base from MediaPipe interim parquets.

Reads `data/interim/mediapipe_frames/{split}/*.parquet`, computes frame and
window features and persists `data/processed/{frame,window}_features_real.*`
plus a `data_quality_report.json`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import get_project_paths
from .extract_runner import MANIFEST_NAME
from .feature_engineering_real import (
    PIPELINE_VERSION,
    aggregate_window_features_real,
    build_frame_features,
    compute_quality_report,
)


def _read_split_parquets(interim_dir: Path, split: str) -> pd.DataFrame:
    split_dir = interim_dir / split
    if not split_dir.exists():
        return pd.DataFrame()
    files = [p for p in sorted(split_dir.glob("*.parquet")) if p.name != MANIFEST_NAME]
    if not files:
        return pd.DataFrame()
    frames = [pd.read_parquet(p) for p in files]
    df = pd.concat(frames, ignore_index=True)
    df["source_split"] = split
    return df


def _read_manifest(interim_dir: Path) -> pd.DataFrame:
    manifest_path = interim_dir / MANIFEST_NAME
    if not manifest_path.exists():
        return pd.DataFrame(columns=["video_id", "split", "frame_stride"])
    try:
        return pd.read_parquet(manifest_path)
    except Exception:
        return pd.DataFrame(columns=["video_id", "split", "frame_stride"])


def build_processed_base(
    interim_dir: Path | None = None,
    output_dir: Path | None = None,
    window_size: int = 15,
    splits: tuple[str, ...] = ("training", "testing"),
) -> dict[str, Any]:
    """Build and persist the processed analytical base for Fase 4."""
    paths = get_project_paths()
    interim_dir = Path(interim_dir) if interim_dir is not None else paths.interim_mediapipe_frames
    output_dir = Path(output_dir) if output_dir is not None else paths.data_processed
    output_dir.mkdir(parents=True, exist_ok=True)

    parts: list[pd.DataFrame] = []
    for split in splits:
        df_split = _read_split_parquets(interim_dir, split)
        if not df_split.empty:
            parts.append(df_split)

    if not parts:
        raise RuntimeError(f"Nenhum parquet encontrado em {interim_dir}. Rode a extração da Fase 3 primeiro.")

    frames_raw = pd.concat(parts, ignore_index=True)
    extraction_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    frame_features = build_frame_features(frames_raw, window_size=window_size)

    # Lineage join: source_split + frame_stride from manifest
    split_map = frames_raw[["video_id", "source_split"]].drop_duplicates()
    frame_features = frame_features.merge(split_map, on="video_id", how="left")

    manifest = _read_manifest(interim_dir)
    if not manifest.empty and "frame_stride" in manifest.columns:
        manifest_subset = manifest[["video_id", "split", "frame_stride"]].rename(columns={"split": "source_split"})
        frame_features = frame_features.merge(manifest_subset, on=["video_id", "source_split"], how="left")
    else:
        frame_features["frame_stride"] = pd.NA

    frame_features["window_size"] = int(window_size)
    frame_features["pipeline_version"] = PIPELINE_VERSION
    frame_features["extraction_timestamp"] = extraction_timestamp

    window_features = aggregate_window_features_real(frame_features)
    window_features["pipeline_version"] = PIPELINE_VERSION
    window_features["window_size"] = int(window_size)
    window_features["extraction_timestamp"] = extraction_timestamp

    frame_parquet = output_dir / "frame_features_real.parquet"
    frame_csv = output_dir / "frame_features_real.csv"
    window_parquet = output_dir / "window_features_real.parquet"
    window_csv = output_dir / "window_features_real.csv"
    quality_path = output_dir / "data_quality_report.json"

    frame_features.to_parquet(frame_parquet, index=False)
    frame_features.to_csv(frame_csv, index=False)
    window_features.to_parquet(window_parquet, index=False)
    window_features.to_csv(window_csv, index=False)

    report = compute_quality_report(frame_features, window_features)
    report["extraction_timestamp"] = extraction_timestamp
    with quality_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    return {
        "frames": int(len(frame_features)),
        "windows": int(len(window_features)),
        "videos": int(frame_features["video_id"].nunique()),
        "splits": list(splits),
        "output_dir": str(output_dir),
        "frame_features_path": str(frame_parquet),
        "window_features_path": str(window_parquet),
        "quality_report_path": str(quality_path),
    }
