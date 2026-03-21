from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FrameMetadata:
    video_id: str
    frame_index: int
    timestamp_seconds: float
    window_id: int


def build_synthetic_frame_metadata(
    video_id: str = "demo_video",
    total_frames: int = 90,
    fps: float = 15.0,
    window_size: int = 15,
) -> pd.DataFrame:
    frames: list[dict[str, str | int | float]] = []
    for frame_index in range(total_frames):
        frames.append(
            asdict(
                FrameMetadata(
                    video_id=video_id,
                    frame_index=frame_index,
                    timestamp_seconds=frame_index / fps,
                    window_id=frame_index // window_size,
                )
            )
        )
    return pd.DataFrame(frames)


def inspect_video_file(video_path: Path) -> dict[str, str | int | bool]:
    return {
        "path": str(video_path),
        "exists": video_path.exists(),
        "suffix": video_path.suffix.lower(),
        "name": video_path.name,
    }
