from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "people_count_mean",
    "movement_score_mean",
    "estimated_speed_mean",
    "dense_scene_rate",
    "suspicious_loitering_rate",
    "risk_score_mean",
]


def run_unsupervised_baseline(features: pd.DataFrame) -> pd.DataFrame:
    result = features.copy()
    result["cluster_id"] = np.select(
        [
            result["dense_scene_rate"] >= 0.5,
            result["risk_score_mean"] >= result["risk_score_mean"].median(),
        ],
        [1, 2],
        default=0,
    )

    anomaly_threshold = result["risk_score_mean"].quantile(0.8)
    result["anomaly_flag"] = np.where(result["risk_score_mean"] >= anomaly_threshold, -1, 1)
    result["anomaly_score"] = result["risk_score_mean"] - result["risk_score_mean"].mean()
    return result
