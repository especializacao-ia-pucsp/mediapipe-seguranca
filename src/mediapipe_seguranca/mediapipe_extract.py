from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

FRAME_SCHEMA: list[str] = [
    "video_id",
    "frame_index",
    "num_people_detected",
    "mean_pose_visibility",
    "bbox_area_total",
    "mean_bbox_area",
    "motion_proxy",
    "detector_fallback_used",
]


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


# ---------------------------------------------------------------------------
# Real MediaPipe extraction
# ---------------------------------------------------------------------------


def _empty_frame_record() -> dict[str, Any]:
    return {
        "video_id": "",
        "frame_index": 0,
        "num_people_detected": 0,
        "mean_pose_visibility": float("nan"),
        "bbox_area_total": 0.0,
        "mean_bbox_area": float("nan"),
        "motion_proxy": 0.0,
        "detector_fallback_used": False,
    }


class MediaPipeExtractor:
    """Wrap MediaPipe Pose Landmarker (primary) + Object Detector (fallback)."""

    def __init__(
        self,
        model_dir: Path,
        num_poses: int = 6,
        det_conf: float = 0.5,
        enable_detector_fallback: bool = True,
    ) -> None:
        # Imports locais para que o módulo possa ser importado sem mediapipe instalado
        # (testes unitários mockam a classe e nunca chegam aqui).
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        self._mp = mp
        self._mp_vision = mp_vision
        self._num_poses = num_poses
        self._det_conf = det_conf

        pose_path = Path(model_dir) / "pose_landmarker_lite.task"
        if not pose_path.exists():
            raise FileNotFoundError(
                f"Modelo Pose Landmarker não encontrado em {pose_path}. " "Rode scripts/download_mediapipe_models.py."
            )

        pose_options = mp_vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(pose_path)),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_poses=num_poses,
        )
        self._pose = mp_vision.PoseLandmarker.create_from_options(pose_options)

        self._detector = None
        det_path = Path(model_dir) / "efficientdet_lite0.tflite"
        if enable_detector_fallback and det_path.exists():
            det_options = mp_vision.ObjectDetectorOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(det_path)),
                running_mode=mp_vision.RunningMode.IMAGE,
                score_threshold=det_conf,
                category_allowlist=["person"],
            )
            self._detector = mp_vision.ObjectDetector.create_from_options(det_options)

    # ------------------------------------------------------------------
    # Context manager helpers
    # ------------------------------------------------------------------
    def __enter__(self) -> "MediaPipeExtractor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        for attr in ("_pose", "_detector"):
            obj = getattr(self, attr, None)
            if obj is not None:
                try:
                    obj.close()
                except Exception:  # pragma: no cover - defensive
                    pass
                setattr(self, attr, None)

    # ------------------------------------------------------------------
    # Frame extraction
    # ------------------------------------------------------------------
    def extract_frame(
        self,
        image_bgr: np.ndarray,
        prev_gray: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """Run pose + (optional) detector on a single BGR frame."""
        import cv2

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = rgb.shape[:2]
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)

        record = _empty_frame_record()

        pose_result = self._pose.detect(mp_image)
        pose_landmarks = getattr(pose_result, "pose_landmarks", []) or []
        num_people = len(pose_landmarks)

        if num_people > 0:
            visibilities: list[float] = []
            bbox_areas: list[float] = []
            for landmarks in pose_landmarks:
                xs = [lm.x for lm in landmarks]
                ys = [lm.y for lm in landmarks]
                visibilities.extend(getattr(lm, "visibility", 0.0) for lm in landmarks)
                if xs and ys:
                    x_min, x_max = max(min(xs), 0.0), min(max(xs), 1.0)
                    y_min, y_max = max(min(ys), 0.0), min(max(ys), 1.0)
                    area = max(x_max - x_min, 0.0) * max(y_max - y_min, 0.0) * width * height
                    bbox_areas.append(float(area))
            record["num_people_detected"] = int(num_people)
            record["mean_pose_visibility"] = float(np.mean(visibilities)) if visibilities else float("nan")
            record["bbox_area_total"] = float(sum(bbox_areas))
            record["mean_bbox_area"] = float(np.mean(bbox_areas)) if bbox_areas else float("nan")

        # Fallback for empty pose detection
        if record["num_people_detected"] == 0 and self._detector is not None:
            det_result = self._detector.detect(mp_image)
            det_areas: list[float] = []
            count = 0
            for detection in getattr(det_result, "detections", []) or []:
                # Filter person + score (categoria já aplicada via allowlist, mas mantemos guarda)
                category = detection.categories[0] if detection.categories else None
                if category is None:
                    continue
                if category.category_name != "person":
                    continue
                if category.score < self._det_conf:
                    continue
                bbox = detection.bounding_box
                area = float(max(bbox.width, 0) * max(bbox.height, 0))
                det_areas.append(area)
                count += 1
            if count > 0:
                record["num_people_detected"] = count
                record["bbox_area_total"] = float(sum(det_areas))
                record["mean_bbox_area"] = float(np.mean(det_areas))
                record["detector_fallback_used"] = True

        # Motion proxy
        if prev_gray is not None:
            curr_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            record["motion_proxy"] = float(np.mean(np.abs(curr_gray.astype(np.int32) - prev_gray.astype(np.int32))))
        else:
            record["motion_proxy"] = 0.0

        return record


def _to_gray(image_bgr: np.ndarray) -> np.ndarray:
    import cv2

    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def extract_video(
    extractor: MediaPipeExtractor,
    frames: Iterable[tuple[int, np.ndarray]],
    video_id: str,
    frame_stride: int = 5,
) -> pd.DataFrame:
    """Run ``extractor`` over a stream of frames and return a tidy DataFrame."""
    if frame_stride < 1:
        raise ValueError("frame_stride deve ser >= 1")

    rows: list[dict[str, Any]] = []
    prev_gray: np.ndarray | None = None

    for frame_index, image in frames:
        if frame_index % frame_stride != 0:
            continue
        record = extractor.extract_frame(image, prev_gray=prev_gray)
        record["video_id"] = video_id
        record["frame_index"] = int(frame_index)
        rows.append({key: record[key] for key in FRAME_SCHEMA})
        prev_gray = _to_gray(image)

    df = pd.DataFrame(rows, columns=FRAME_SCHEMA)
    if df.empty:
        # Build empty df with correct dtypes so downstream concat works.
        df = df.astype(
            {
                "video_id": "object",
                "frame_index": "int64",
                "num_people_detected": "int64",
                "mean_pose_visibility": "float64",
                "bbox_area_total": "float64",
                "mean_bbox_area": "float64",
                "motion_proxy": "float64",
                "detector_fallback_used": "bool",
            }
        )
        return df

    df = df.astype(
        {
            "video_id": "object",
            "frame_index": "int64",
            "num_people_detected": "int64",
            "bbox_area_total": "float64",
            "mean_bbox_area": "float64",
            "mean_pose_visibility": "float64",
            "motion_proxy": "float64",
            "detector_fallback_used": "bool",
        }
    )
    return df
