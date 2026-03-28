"""
Create a minimal synthetic ShanghaiTech-compatible dataset for pipeline testing.

Generates:
  - 5 training "videos" (50 frames each, 320x240 RGB JPEG)
  - 2 testing "videos" (30 frames each)
  - 2 GT mask .npy files (0=normal, 1=anomaly for ~20% of frames)

Output: data/raw/shanghaitech/SAMPLE/
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    print("opencv-python-headless is required. Installing…")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python-headless"])
    import cv2  # noqa: F811  # re-import after install

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = PROJECT_ROOT / "data" / "raw" / "shanghaitech" / "SAMPLE"

TRAIN_VIDEOS = 5
TRAIN_FRAMES = 50
TEST_VIDEOS = 2
TEST_FRAMES = 30
FRAME_W, FRAME_H = 320, 240

ANOMALY_RATIO = 0.2  # fraction of test frames marked as anomaly

# ---------------------------------------------------------------------------
# Frame generation helpers
# ---------------------------------------------------------------------------


def _make_normal_frame(frame_idx: int, video_idx: int) -> np.ndarray:
    """Generate a synthetic normal frame — slow-moving background gradient."""
    rng = np.random.default_rng(seed=video_idx * 10000 + frame_idx)
    img = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
    # Smooth gradient background
    base_color = rng.integers(40, 120, size=3, dtype=np.uint8)
    phase = frame_idx / TRAIN_FRAMES * 2 * np.pi
    shift = int(10 * np.sin(phase))
    img[:, :] = base_color
    # Walking person (rectangle) moving horizontally
    person_x = (frame_idx * 4 + video_idx * 30) % (FRAME_W - 20)
    person_y = FRAME_H // 2 - 20
    cv2.rectangle(img, (person_x, person_y), (person_x + 15, person_y + 40), (180, 120, 80), -1)
    # Add slight noise
    noise = rng.integers(0, 15, size=img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    _ = shift  # suppress unused
    return img


def _make_anomaly_frame(frame_idx: int, video_idx: int) -> np.ndarray:
    """Generate a synthetic anomaly frame — running person (brighter, different pose)."""
    rng = np.random.default_rng(seed=video_idx * 10000 + frame_idx + 99999)
    img = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
    base_color = rng.integers(40, 120, size=3, dtype=np.uint8)
    img[:, :] = base_color
    # Running person — larger bounding box, faster
    person_x = (frame_idx * 12 + video_idx * 30) % (FRAME_W - 25)
    person_y = FRAME_H // 3
    cv2.rectangle(img, (person_x, person_y), (person_x + 20, person_y + 50), (80, 80, 220), -1)
    # Second person (crowd)
    cv2.rectangle(img, (person_x + 30, person_y + 5), (person_x + 45, person_y + 45), (90, 200, 90), -1)
    noise = rng.integers(0, 20, size=img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    return img


# ---------------------------------------------------------------------------
# Create training videos
# ---------------------------------------------------------------------------


def _create_training(root: Path) -> list[Path]:
    frames_root = root / "training" / "frames"
    video_paths: list[Path] = []
    print(f"Creating {TRAIN_VIDEOS} synthetic training videos ({TRAIN_FRAMES} frames each)…")
    for v_idx in range(TRAIN_VIDEOS):
        video_name = f"01_{v_idx + 1:03d}"
        video_dir = frames_root / video_name
        video_dir.mkdir(parents=True, exist_ok=True)
        for f_idx in range(TRAIN_FRAMES):
            frame = _make_normal_frame(f_idx, v_idx)
            frame_path = video_dir / f"{f_idx:03d}.jpg"
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        video_paths.append(video_dir)
        print(f"  [{v_idx + 1}/{TRAIN_VIDEOS}] {video_name} — {TRAIN_FRAMES} frames")
    return video_paths


# ---------------------------------------------------------------------------
# Create testing videos + GT masks
# ---------------------------------------------------------------------------


def _create_testing(root: Path) -> list[tuple[Path, Path]]:
    frames_root = root / "testing" / "frames"
    masks_root = root / "testing" / "test_frame_mask"
    frames_root.mkdir(parents=True, exist_ok=True)
    masks_root.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, Path]] = []
    print(f"\nCreating {TEST_VIDEOS} synthetic testing videos ({TEST_FRAMES} frames each)…")

    for v_idx in range(TEST_VIDEOS):
        video_name = f"01_{v_idx + 1:04d}"
        video_dir = frames_root / video_name
        video_dir.mkdir(parents=True, exist_ok=True)

        # Build GT mask: 0 = normal, 1 = anomaly
        rng_gt = random.Random(42 + v_idx)
        gt = np.zeros(TEST_FRAMES, dtype=np.uint8)
        anomaly_start = int(TEST_FRAMES * 0.6)
        anomaly_end = int(TEST_FRAMES * (0.6 + ANOMALY_RATIO))
        gt[anomaly_start:anomaly_end] = 1

        for f_idx in range(TEST_FRAMES):
            is_anomaly = bool(gt[f_idx])
            if is_anomaly:
                frame = _make_anomaly_frame(f_idx, v_idx)
            else:
                frame = _make_normal_frame(f_idx, v_idx + TRAIN_VIDEOS)
            frame_path = video_dir / f"{f_idx:03d}.jpg"
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

        mask_path = masks_root / f"{video_name}.npy"
        np.save(str(mask_path), gt)

        anomaly_count = int(gt.sum())
        print(f"  [{v_idx + 1}/{TEST_VIDEOS}] {video_name} — {TEST_FRAMES} frames, {anomaly_count} anomaly frames")
        _ = rng_gt  # suppress unused
        results.append((video_dir, mask_path))

    return results


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def _write_sample_readme(root: Path, train_paths: list[Path], test_results: list[tuple[Path, Path]]) -> None:
    total_frames = TRAIN_VIDEOS * TRAIN_FRAMES + TEST_VIDEOS * TEST_FRAMES
    content = f"""# ShanghaiTech SAMPLE — Synthetic Mini Dataset

This is a **synthetic mini dataset** generated for pipeline development and testing.
It mimics the structure of the real ShanghaiTech Campus dataset without requiring
the download of the full ~17 GB dataset.

## Contents

- **Training**: {len(train_paths)} videos × {TRAIN_FRAMES} frames = {TRAIN_VIDEOS * TRAIN_FRAMES} frames
- **Testing**: {len(test_results)} videos × {TEST_FRAMES} frames = {TEST_VIDEOS * TEST_FRAMES} frames
- **GT masks**: {len(test_results)} .npy files (0=normal, 1=anomaly)
- **Total frames**: {total_frames} JPEG images ({FRAME_W}×{FRAME_H})
- **Anomaly ratio in test**: {ANOMALY_RATIO:.0%} of frames

## Structure

```
SAMPLE/
    training/frames/01_001/ ... 01_00{TRAIN_VIDEOS}/
    testing/frames/01_0001/ ... 01_000{TEST_VIDEOS}/
    testing/test_frame_mask/01_0001.npy ... 01_000{TEST_VIDEOS}.npy
```

## Usage

The `shanghaitech_loader.py` module will automatically prefer the real dataset
if available, or fall back to `SAMPLE/` for development.

To regenerate:
```bash
.venv\\Scripts\\python.exe scripts/create_sample_shanghaitech.py
```
"""
    (root / "SAMPLE_README.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("Creating Synthetic ShanghaiTech SAMPLE Dataset")
    print("=" * 60)
    print(f"Output: {SAMPLE_ROOT}")

    SAMPLE_ROOT.mkdir(parents=True, exist_ok=True)

    train_paths = _create_training(SAMPLE_ROOT)
    test_results = _create_testing(SAMPLE_ROOT)
    _write_sample_readme(SAMPLE_ROOT, train_paths, test_results)

    total_frames = sum(len(list(p.glob("*.jpg"))) for p in train_paths) + sum(
        len(list(vd.glob("*.jpg"))) for vd, _ in test_results
    )

    print(f"\nDone! {total_frames} synthetic frames created in {SAMPLE_ROOT}")
    print(f"  Training videos: {len(train_paths)}")
    print(f"  Testing videos : {len(test_results)}")
    print(f"  GT mask files  : {len(test_results)}")


if __name__ == "__main__":
    main()
