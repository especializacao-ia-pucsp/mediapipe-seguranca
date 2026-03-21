from __future__ import annotations

import pandas as pd


def enrich_frame_features(frame_observations: pd.DataFrame) -> pd.DataFrame:
    enriched = frame_observations.copy()
    enriched["occupancy_score"] = enriched["people_count"] * (1 + enriched["dense_scene"] * 0.5)
    enriched["risk_score"] = (
        enriched["movement_score"] * 0.35
        + enriched["estimated_speed"] * 0.30
        + enriched["fall_risk_score"] * 0.20
        + enriched["suspicious_loitering"] * 0.15
    )
    enriched["motion_intensity"] = enriched["movement_score"] * enriched["estimated_speed"]
    return enriched
