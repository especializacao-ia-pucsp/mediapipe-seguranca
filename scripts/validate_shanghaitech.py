#!/usr/bin/env python
"""
Validate ShanghaiTech Campus dataset structure and print a status report.
Run from project root: python scripts/validate_shanghaitech.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mediapipe_seguranca.shanghaitech_loader import (
    _resolve_dataset_root,
    _shanghaitech_root,
    get_test_videos_with_gt,
    get_train_videos,
    iter_frames,
    load_gt_mask,
)


def main() -> None:
    # Ensure UTF-8 output on Windows terminals
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    root = _shanghaitech_root()
    active = _resolve_dataset_root()
    is_sample = "SAMPLE" in str(active)

    print("=" * 60)
    print("ShanghaiTech Campus -- Dataset Validation Report")
    print("=" * 60)
    print(f"Dataset root  : {root}")
    print(f"Active root   : {active}")
    print(f"Using         : {'SAMPLE (synthetic)' if is_sample else 'REAL dataset'}")
    print()

    train = get_train_videos()
    test = get_test_videos_with_gt()

    print(f"Training videos : {len(train)}")
    print(f"Test pairs (video+GT) : {len(test)}")

    if train:
        sample_frames = list(iter_frames(train[0]))
        print(f"Frames in first train video: {len(sample_frames)}")

    if test:
        gt = load_gt_mask(test[0][1])
        normal = int((gt == 0).sum())
        anomaly = int((gt == 1).sum())
        print(f"GT mask of first test video: {len(gt)} frames ({normal} normal, {anomaly} anomalous)")

    print()
    if is_sample:
        print("[OK]  SAMPLE dataset ready (synthetic -- suitable for pipeline development)")
        print("[!!]  Real dataset not present -- see DOWNLOAD_INSTRUCTIONS.md")
    elif len(train) >= 300:
        print("[OK]  Real dataset: COMPLETE")
    elif len(train) > 0:
        print(f"[!!]  Data present but incomplete ({len(train)} train videos -- expected ~330)")
    else:
        print("[FAIL] No dataset found. Run: python scripts/create_sample_shanghaitech.py")

    print("=" * 60)


if __name__ == "__main__":
    main()
