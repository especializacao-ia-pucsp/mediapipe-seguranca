"""Download MediaPipe Tasks model files used by the extraction pipeline.

Models are downloaded into ``models/mediapipe/`` (relative to repo root):

* ``pose_landmarker_lite.task`` — Pose Landmarker (primary detector).
* ``efficientdet_lite0.tflite`` — Object Detector (person fallback).

Usage::

    python scripts/download_mediapipe_models.py
    python scripts/download_mediapipe_models.py --force
"""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

MODEL_URLS: dict[str, str] = {
    "pose_landmarker_lite.task": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
    ),
    "efficientdet_lite0.tflite": (
        "https://storage.googleapis.com/mediapipe-models/object_detector/"
        "efficientdet_lite0/int8/latest/efficientdet_lite0.tflite"
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_target_dir() -> Path:
    return _repo_root() / "models" / "mediapipe"


def download_model(filename: str, url: str, target_dir: Path, force: bool = False) -> Path:
    """Download a single model file via HTTPS into ``target_dir``."""
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    if target_path.exists() and not force:
        size_mb = target_path.stat().st_size / (1024 * 1024)
        print(f"[skip] {filename} já existe ({size_mb:.2f} MB) em {target_path}")
        return target_path

    print(f"[down] {filename}\n        de {url}")
    urllib.request.urlretrieve(url, target_path)  # noqa: S310 (URLs fixas e confiáveis)
    size_mb = target_path.stat().st_size / (1024 * 1024)
    print(f"[ok  ] {filename} salvo em {target_path} ({size_mb:.2f} MB)")
    return target_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baixa modelos MediaPipe Tasks.")
    parser.add_argument("--force", action="store_true", help="Reescrever se já existirem.")
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Diretório destino (default: models/mediapipe/).",
    )
    args = parser.parse_args(argv)

    target_dir = args.target_dir or _default_target_dir()
    for filename, url in MODEL_URLS.items():
        download_model(filename, url, target_dir, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
