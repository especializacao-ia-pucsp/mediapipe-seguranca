# ShanghaiTech SAMPLE — Synthetic Mini Dataset

This is a **synthetic mini dataset** generated for pipeline development and testing.
It mimics the structure of the real ShanghaiTech Campus dataset without requiring
the download of the full ~17 GB dataset.

## Contents

- **Training**: 5 videos × 50 frames = 250 frames
- **Testing**: 2 videos × 30 frames = 60 frames
- **GT masks**: 2 .npy files (0=normal, 1=anomaly)
- **Total frames**: 310 JPEG images (320×240)
- **Anomaly ratio in test**: 20% of frames

## Structure

```
SAMPLE/
    training/frames/01_001/ ... 01_005/
    testing/frames/01_0001/ ... 01_0002/
    testing/test_frame_mask/01_0001.npy ... 01_0002.npy
```

## Usage

The `shanghaitech_loader.py` module will automatically prefer the real dataset
if available, or fall back to `SAMPLE/` for development.

To regenerate:
```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```
