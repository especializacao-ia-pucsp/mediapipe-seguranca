from __future__ import annotations

import pandas as pd


def aggregate_window_features(frame_features: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        frame_features.groupby("window_id", as_index=False)
        .agg(
            people_count_mean=("people_count", "mean"),
            people_count_max=("people_count", "max"),
            movement_score_mean=("movement_score", "mean"),
            posture_change_rate_mean=("posture_change_rate", "mean"),
            estimated_speed_mean=("estimated_speed", "mean"),
            dense_scene_rate=("dense_scene", "mean"),
            suspicious_loitering_rate=("suspicious_loitering", "mean"),
            fall_risk_score_mean=("fall_risk_score", "mean"),
            occupancy_score_mean=("occupancy_score", "mean"),
            risk_score_mean=("risk_score", "mean"),
            motion_intensity_mean=("motion_intensity", "mean"),
            label=("label", lambda values: values.mode().iat[0]),
        )
    )
    grouped["event_count"] = 1
    return grouped
