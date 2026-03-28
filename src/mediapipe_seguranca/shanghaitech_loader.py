"""
ShanghaiTech Campus Dataset loader for the MediaPipe Segurança pipeline.

Provides generators and loaders for training frames, test frames, and
frame-level ground-truth masks.  Works with both the real dataset and the
synthetic SAMPLE/ directory created by scripts/create_sample_shanghaitech.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import numpy as np

from mediapipe_seguranca.config import get_project_paths

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _shanghaitech_root() -> Path:
    """Return the shanghaitech directory under data/raw/."""
    return get_project_paths().data_raw / "shanghaitech"


def _resolve_dataset_root() -> Path:
    """
    Return the active dataset root.

     Priority:
     1. Real dataset if it has minimum coherent structure
         (>=1 train dir, >=1 test dir, >=1 test .npy mask)
     2. SAMPLE dataset: SAMPLE/training/frames/ exists
    """
    root = _shanghaitech_root()

    real_train = root / "training" / "frames"
    real_test = root / "testing" / "frames"
    real_masks = root / "testing" / "test_frame_mask"
    real_ready = (
        real_train.exists()
        and any(p.is_dir() for p in real_train.iterdir())
        and real_test.exists()
        and any(p.is_dir() for p in real_test.iterdir())
        and real_masks.exists()
        and any(real_masks.glob("*.npy"))
    )

    if real_ready:
        return root

    sample_train = root / "SAMPLE" / "training" / "frames"
    if sample_train.exists() and any(sample_train.iterdir()):
        return root / "SAMPLE"
    # Fall back to real root even if empty (caller will get empty lists)
    return root


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_train_videos() -> list[Path]:
    """
    Return sorted list of paths to training video frame directories.

    Each path is a directory containing JPEG frames (e.g. 000.jpg, 001.jpg …).

    Returns
    -------
    list[Path]
        Empty list if the dataset has not been downloaded/generated.
    """
    root = _resolve_dataset_root()
    train_frames_dir = root / "training" / "frames"
    if not train_frames_dir.exists():
        return []
    return sorted(p for p in train_frames_dir.iterdir() if p.is_dir())


def get_test_videos_with_gt() -> list[tuple[Path, Path]]:
    """
    Return list of (frames_dir, gt_npy_path) tuples for the test set.

    Only videos that have a matching .npy ground-truth mask are included.

    Returns
    -------
    list[tuple[Path, Path]]
        Each element is (video_frames_dir, gt_mask_path).
    """
    root = _resolve_dataset_root()
    test_frames_dir = root / "testing" / "frames"
    masks_dir = root / "testing" / "test_frame_mask"

    if not test_frames_dir.exists() or not masks_dir.exists():
        return []

    result: list[tuple[Path, Path]] = []
    for video_dir in sorted(p for p in test_frames_dir.iterdir() if p.is_dir()):
        mask_path = masks_dir / f"{video_dir.name}.npy"
        if mask_path.exists():
            result.append((video_dir, mask_path))
    return result


def load_gt_mask(npy_path: Path) -> np.ndarray:
    """
    Load a frame-level ground-truth mask from a .npy file.

    Parameters
    ----------
    npy_path : Path
        Path to a .npy file containing a 1-D uint8 array where
        0 = normal frame, 1 = anomalous frame.

    Returns
    -------
    np.ndarray
        Shape (n_frames,), dtype uint8.
    """
    mask: np.ndarray = np.load(str(npy_path))
    return mask.flatten().astype(np.uint8)


def iter_frames(video_dir: Path) -> Generator[tuple[int, Path], None, None]:
    """
    Yield (frame_index, frame_path) pairs for every JPEG in a video directory.

    Frames are yielded in lexicographic order (000.jpg, 001.jpg, …).

    Parameters
    ----------
    video_dir : Path
        Directory containing per-frame JPEG images.

    Yields
    ------
    tuple[int, Path]
        (zero-based frame index, path to the .jpg file)
    """
    frames = sorted(video_dir.glob("*.jpg"))
    for idx, frame_path in enumerate(frames):
        yield idx, frame_path
