from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class FrameObservation:
    frame_index: int
    window_id: int
    people_count: int
    movement_score: float
    posture_change_rate: float
    estimated_speed: float
    dense_scene: int
    fall_risk_score: float
    suspicious_loitering: int
    label: str


def generate_demo_observations(frame_metadata: pd.DataFrame) -> pd.DataFrame:
    observations: list[dict[str, int | float | str]] = []

    for row in frame_metadata.itertuples(index=False):
        phase = row.window_id
        if phase in (0, 1):
            people_count = 1 + (row.frame_index % 2)
            movement_score = 0.18 + (row.frame_index % 3) * 0.03
            posture_change_rate = 0.10
            estimated_speed = 0.35
            dense_scene = 0
            fall_risk_score = 0.02
            suspicious_loitering = 0
            label = "normal"
        elif phase in (2, 3):
            people_count = 4 + (row.frame_index % 3)
            movement_score = 0.52 + (row.frame_index % 4) * 0.06
            posture_change_rate = 0.18
            estimated_speed = 0.82
            dense_scene = 1
            fall_risk_score = 0.06
            suspicious_loitering = 0
            label = "aglomeracao"
        else:
            people_count = 1
            movement_score = 0.68 if row.frame_index % 2 == 0 else 0.24
            posture_change_rate = 0.42
            estimated_speed = 1.12 if row.frame_index % 2 == 0 else 0.08
            dense_scene = 0
            fall_risk_score = 0.31 if row.frame_index % 5 == 0 else 0.11
            suspicious_loitering = 1 if row.frame_index % 4 == 0 else 0
            label = "evento_risco"

        observations.append(
            asdict(
                FrameObservation(
                    frame_index=row.frame_index,
                    window_id=row.window_id,
                    people_count=people_count,
                    movement_score=movement_score,
                    posture_change_rate=posture_change_rate,
                    estimated_speed=estimated_speed,
                    dense_scene=dense_scene,
                    fall_risk_score=fall_risk_score,
                    suspicious_loitering=suspicious_loitering,
                    label=label,
                )
            )
        )

    return pd.DataFrame(observations)
