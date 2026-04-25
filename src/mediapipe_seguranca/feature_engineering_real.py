"""Feature engineering nativo dos sinais reais extraídos pelo MediaPipe.

Substitui o adaptador heurístico antigo (`_adapt_real_frames_to_features`)
e produz a base analítica da Fase 4 a partir do `FRAME_SCHEMA` da extração.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

PIPELINE_VERSION = "fase4-v1"
DEFAULT_WINDOW_SIZE = 15

FRAME_FEATURES_SCHEMA: list[str] = [
    "video_id",
    "frame_index",
    "window_id",
    "num_people_detected",
    "mean_pose_visibility",
    "bbox_area_total",
    "mean_bbox_area",
    "motion_proxy",
    "detector_fallback_used",
    "motion_proxy_norm",
    "bbox_area_per_person",
    "is_dense_scene",
    "is_empty_scene",
    "pose_quality",
]

WINDOW_FEATURES_SCHEMA: list[str] = [
    "video_id",
    "window_id",
    "frames_in_window",
    "num_people_detected_mean",
    "num_people_detected_std",
    "num_people_detected_min",
    "num_people_detected_max",
    "people_peak",
    "people_var",
    "mean_pose_visibility_mean",
    "mean_pose_visibility_std",
    "bbox_area_total_mean",
    "bbox_area_total_std",
    "mean_bbox_area_mean",
    "mean_bbox_area_std",
    "motion_proxy_mean",
    "motion_proxy_std",
    "motion_proxy_norm_mean",
    "motion_proxy_norm_std",
    "motion_delta",
    "bbox_area_per_person_mean",
    "pose_quality_mean",
    "empty_scene_rate",
    "dense_scene_rate",
    "fallback_rate",
]


def _normalize_motion(group: pd.Series) -> pd.Series:
    motion = group.fillna(0.0).astype(float)
    max_value = motion.max()
    if max_value and max_value > 0:
        return motion / max_value
    return pd.Series(np.zeros(len(motion), dtype=float), index=motion.index)


def build_frame_features(
    frames_df: pd.DataFrame,
    window_size: int = DEFAULT_WINDOW_SIZE,
) -> pd.DataFrame:
    """Compute frame-level analytical features from raw extraction parquet."""
    if window_size <= 0:
        raise ValueError("window_size deve ser > 0")

    if frames_df.empty:
        return pd.DataFrame(columns=FRAME_FEATURES_SCHEMA)

    df = frames_df.copy()
    df["num_people_detected"] = df["num_people_detected"].fillna(0).astype("int64")
    df["bbox_area_total"] = df["bbox_area_total"].fillna(0.0).astype(float)
    df["mean_bbox_area"] = df["mean_bbox_area"].astype(float)
    df["motion_proxy"] = df["motion_proxy"].astype(float)
    df["mean_pose_visibility"] = df["mean_pose_visibility"].astype(float)
    df["detector_fallback_used"] = df["detector_fallback_used"].fillna(False).astype(bool)
    df["frame_index"] = df["frame_index"].astype("int64")

    df["window_id"] = (df["frame_index"] // window_size).astype("int64")

    df["motion_proxy_norm"] = (
        df.groupby("video_id", group_keys=False)["motion_proxy"].apply(_normalize_motion).astype(float)
    )

    people_safe = df["num_people_detected"].clip(lower=1)
    bbox_per_person = df["bbox_area_total"] / people_safe
    df["bbox_area_per_person"] = np.where(df["num_people_detected"] > 0, bbox_per_person, 0.0).astype(float)

    df["is_dense_scene"] = (df["num_people_detected"] >= 4).astype(bool)
    df["is_empty_scene"] = (df["num_people_detected"] == 0).astype(bool)
    df["pose_quality"] = df["mean_pose_visibility"].astype(float)

    return df[FRAME_FEATURES_SCHEMA].reset_index(drop=True)


def aggregate_window_features_real(frame_features: pd.DataFrame) -> pd.DataFrame:
    """Aggregate frame-level features into per-(video, window) rows."""
    if frame_features.empty:
        return pd.DataFrame(columns=WINDOW_FEATURES_SCHEMA)

    numeric_cols = [
        "num_people_detected",
        "mean_pose_visibility",
        "bbox_area_total",
        "mean_bbox_area",
        "motion_proxy",
        "motion_proxy_norm",
    ]

    grouped = frame_features.groupby(["video_id", "window_id"], sort=True)

    agg_dict: dict[str, list[str]] = {col: ["mean", "std", "min", "max"] for col in numeric_cols}
    base = grouped.agg(agg_dict)
    base.columns = [f"{col}_{stat}" for col, stat in base.columns]
    base = base.reset_index()

    extras = grouped.agg(
        frames_in_window=("frame_index", "count"),
        people_peak=("num_people_detected", "max"),
        people_var=("num_people_detected", "var"),
        empty_scene_rate=("is_empty_scene", "mean"),
        dense_scene_rate=("is_dense_scene", "mean"),
        fallback_rate=("detector_fallback_used", "mean"),
        motion_min=("motion_proxy_norm", "min"),
        motion_max=("motion_proxy_norm", "max"),
        bbox_area_per_person_mean=("bbox_area_per_person", "mean"),
        pose_quality_mean=("pose_quality", "mean"),
    ).reset_index()

    merged = base.merge(extras, on=["video_id", "window_id"])
    merged["motion_delta"] = (merged["motion_max"] - merged["motion_min"]).astype(float)
    merged["people_peak"] = merged["people_peak"].astype("int64")
    merged["frames_in_window"] = merged["frames_in_window"].astype("int64")
    # people_var is already NaN when count == 1 (pandas default ddof=1)

    return merged[WINDOW_FEATURES_SCHEMA].reset_index(drop=True)


def _to_python(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if np.isnan(f) else f
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def compute_quality_report(frames: pd.DataFrame, windows: pd.DataFrame) -> dict[str, Any]:
    """Return a JSON-serializable quality report describing the processed base."""
    report: dict[str, Any] = {
        "pipeline_version": PIPELINE_VERSION,
        "extraction_timestamp": None,
        "total_frames": int(len(frames)),
        "total_videos": int(frames["video_id"].nunique()) if not frames.empty else 0,
        "total_windows": int(len(windows)),
        "missing_per_column": {},
        "value_ranges": {},
        "outlier_flags": {},
        "frames_without_detection": 0,
        "frames_with_fallback": 0,
    }

    if frames.empty:
        return report

    if "extraction_timestamp" in frames.columns:
        ts_series = frames["extraction_timestamp"].dropna()
        if not ts_series.empty:
            report["extraction_timestamp"] = str(ts_series.iloc[0])

    float_cols = [
        "mean_pose_visibility",
        "bbox_area_total",
        "mean_bbox_area",
        "motion_proxy",
        "motion_proxy_norm",
        "bbox_area_per_person",
        "pose_quality",
    ]
    numeric_cols = ["num_people_detected", *float_cols]

    for col in float_cols:
        if col in frames.columns:
            report["missing_per_column"][col] = int(frames[col].isna().sum())

    for col in numeric_cols:
        if col in frames.columns:
            series = frames[col].dropna()
            if series.empty:
                report["value_ranges"][col] = {"min": None, "max": None, "mean": None}
            else:
                report["value_ranges"][col] = {
                    "min": _to_python(series.min()),
                    "max": _to_python(series.max()),
                    "mean": _to_python(series.mean()),
                }

    for col in numeric_cols:
        if col not in frames.columns:
            continue
        series = frames[col].dropna()
        if len(series) < 4:
            report["outlier_flags"][col] = 0
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        report["outlier_flags"][col] = int(((series < lower) | (series > upper)).sum())

    report["frames_without_detection"] = int((frames["num_people_detected"] == 0).sum())
    report["frames_with_fallback"] = int(frames["detector_fallback_used"].astype(bool).sum())

    return report
