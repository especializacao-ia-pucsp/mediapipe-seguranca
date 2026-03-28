"""
Download ShanghaiTech Campus Dataset for anomaly detection.

Tries multiple sources in order:
  A) Google Drive folder download via gdown
  B) Google Drive file IDs (tar archives) via gdown
  C) Kaggle API (if configured)
  D) Graceful fallback with manual instructions
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEST = PROJECT_ROOT / "data" / "raw" / "shanghaitech"
TRAINING_FRAMES = DEST / "training" / "frames"
TESTING_FRAMES = DEST / "testing" / "frames"
TESTING_MASKS = DEST / "testing" / "test_frame_mask"
STATUS_FILE = DEST / "DOWNLOAD_STATUS.md"
INSTRUCTIONS_FILE = DEST / "DOWNLOAD_INSTRUCTIONS.md"

# ---------------------------------------------------------------------------
# Source candidates
# ---------------------------------------------------------------------------
# Option A — Google Drive folders (pre-extracted frames shared by researchers)
GDRIVE_TRAIN_FOLDER = "https://drive.google.com/drive/folders/1fPOb0vH7Vy9L4RhSivniQlmxhKa3JXIL"
GDRIVE_TEST_FOLDER = "https://drive.google.com/drive/folders/1njFiC9bO6-A_0AxKQpZKHfF3xUPDiXzc"

# Option B — single archive file IDs
CANDIDATE_TRAIN_IDS: list[str] = [
    "1rymF0gLYjb9K9h0q5BXc3iHMOGMXRnuD",
    "1bN6YV3bpv1wFuPlDR1xh_-P1Ge-B-Ywk",
]
CANDIDATE_TEST_IDS: list[str] = [
    "1UlIjUScPnjijBDHE0LYrXaVAY9v7yLaG",
    "1CbkaqeRK0yEI2I9hMJH4G0CXHV8mvhkJ",
]

# Option C — Kaggle (dataset slug)
KAGGLE_DATASET = "defeatthefake/shanghaitech-campus-dataset"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_dirs() -> None:
    for d in [TRAINING_FRAMES, TESTING_FRAMES, TESTING_MASKS]:
        d.mkdir(parents=True, exist_ok=True)


def _count_images(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for f in directory.rglob("*.jpg")) + sum(1 for f in directory.rglob("*.png"))


def _count_masks(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for f in directory.glob("*.npy"))


def _dataset_looks_complete() -> bool:
    """Return True if the dataset appears to have been downloaded already."""
    train_dirs = list(TRAINING_FRAMES.glob("*")) if TRAINING_FRAMES.exists() else []
    test_dirs = list(TESTING_FRAMES.glob("*")) if TESTING_FRAMES.exists() else []
    masks = list(TESTING_MASKS.glob("*.npy")) if TESTING_MASKS.exists() else []
    return len(train_dirs) >= 50 or (len(test_dirs) >= 10 and len(masks) >= 10)


def _extract_archive(archive: Path, dest: Path) -> bool:
    """Extract a tar/zip archive into dest. Returns True on success."""
    try:
        if tarfile.is_tarfile(archive):
            print(f"  Extracting tar: {archive.name} → {dest}")
            with tarfile.open(archive) as tf:
                tf.extractall(path=dest)
            return True
        elif zipfile.is_zipfile(archive):
            print(f"  Extracting zip: {archive.name} → {dest}")
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(path=dest)
            return True
        else:
            print(f"  Unknown archive format: {archive.name}")
            return False
    except Exception as exc:
        print(f"  Extraction error: {exc}")
        return False


def _gdown_available() -> bool:
    try:
        import gdown  # noqa: F401

        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Strategy A — Google Drive folder download
# ---------------------------------------------------------------------------


def _try_gdrive_folder(url: str, dest: Path, label: str) -> bool:
    if not _gdown_available():
        print("  gdown not installed — skipping folder download")
        return False
    try:
        import gdown

        print(f"  Downloading {label} folder from Google Drive…")
        dest.mkdir(parents=True, exist_ok=True)
        gdown.download_folder(url=url, output=str(dest), quiet=False, use_cookies=False)
        # Count only leaf video subdirectories that actually contain frames
        video_dirs = [p for p in dest.rglob("*") if p.is_dir() and any(p.glob("*.jpg"))]
        if video_dirs:
            print(f"  Downloaded {len(video_dirs)} video directories to {dest}")
            return True
        print("  No video frames found after folder download — treating as failure")
        return False
    except Exception as exc:
        print(f"  Folder download failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Strategy B — Google Drive single file IDs
# ---------------------------------------------------------------------------


def _try_gdrive_file(file_id: str, dest_dir: Path, label: str) -> bool:
    if not _gdown_available():
        print("  gdown not installed — skipping file download")
        return False
    try:
        import gdown

        tmp_path = dest_dir / f"_tmp_{file_id[:8]}.bin"
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"  Downloading {label} from Google Drive (id={file_id[:8]}…)")
        gdown.download(url=url, output=str(tmp_path), quiet=False, use_cookies=False)
        if not tmp_path.exists() or tmp_path.stat().st_size < 1024:
            print("  Downloaded file too small — likely an error page")
            tmp_path.unlink(missing_ok=True)
            return False
        success = _extract_archive(tmp_path, dest_dir)
        tmp_path.unlink(missing_ok=True)
        return success
    except Exception as exc:
        print(f"  File download failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Strategy C — Kaggle API
# ---------------------------------------------------------------------------


def _try_kaggle(dest_dir: Path) -> bool:
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("  No ~/.kaggle/kaggle.json found — skipping Kaggle download")
        return False
    try:
        print(f"  Trying Kaggle dataset: {KAGGLE_DATASET}")
        result = subprocess.run(
            [sys.executable, "-m", "kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "-p", str(dest_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  Kaggle CLI error: {result.stderr[:200]}")
            return False
        # Extract downloaded zip files
        for zf in dest_dir.glob("*.zip"):
            _extract_archive(zf, dest_dir)
            zf.unlink(missing_ok=True)
        return True
    except Exception as exc:
        print(f"  Kaggle download failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Fallback — write instructions
# ---------------------------------------------------------------------------


def _write_instructions() -> None:
    content = """# ShanghaiTech Campus Dataset — Download Instructions

Automatic download failed. Please download the dataset manually.

## Official Source

- Homepage: https://svip-lab.github.io/dataset/campus_dataset.html
- Paper: *Learning Temporal Regularity in Video Sequences* (Rui Luo et al., CVPR 2016)

## Manual Download Steps

1. Visit https://svip-lab.github.io/dataset/campus_dataset.html
2. Download:
   - `training.tar.gz` (training frames — ~17 GB)
   - `testing.tar.gz` (testing frames + frame-level GT masks)
3. Extract both archives into `data/raw/shanghaitech/`:
   ```
   tar xzf training.tar.gz -C data/raw/shanghaitech/
   tar xzf testing.tar.gz  -C data/raw/shanghaitech/
   ```

## Alternative: Academic Torrents / Roboflow / Kaggle

- Search Kaggle for "shanghaitech campus anomaly"
- Search academictorrents.com for "shanghaitech"

## Expected Structure After Extraction

```
data/raw/shanghaitech/
    training/
        frames/
            01_001/   ← ~2000 .jpg frames
            01_002/
            ... (≈330 video sub-folders)
    testing/
        frames/
            01_0014/
            ... (≈107 video sub-folders)
        test_frame_mask/
            01_0014.npy   ← frame-level binary GT (0=normal, 1=anomaly)
            ... (137 .npy files)
```

## Using the Mini Synthetic Dataset (While Waiting)

Run the following to generate a functional mini dataset for pipeline testing:
```bash
.venv\\Scripts\\python.exe scripts/create_sample_shanghaitech.py
```
This creates `data/raw/shanghaitech/SAMPLE/` with synthetic frames and GT masks.
"""
    INSTRUCTIONS_FILE.write_text(content, encoding="utf-8")
    print(f"  Instructions written to {INSTRUCTIONS_FILE}")


# ---------------------------------------------------------------------------
# Status report
# ---------------------------------------------------------------------------


def _write_status(success: bool, method: str) -> None:
    train_dirs = list(TRAINING_FRAMES.glob("*")) if TRAINING_FRAMES.exists() else []
    test_dirs = list(TESTING_FRAMES.glob("*")) if TESTING_FRAMES.exists() else []
    masks = list(TESTING_MASKS.glob("*.npy")) if TESTING_MASKS.exists() else []
    train_imgs = _count_images(TRAINING_FRAMES)
    test_imgs = _count_images(TESTING_FRAMES)

    status = "SUCCESS" if success else "FAILED"
    content = f"""# ShanghaiTech Download Status

- **Status**: {status}
- **Method**: {method}
- **Training video folders**: {len(train_dirs)}
- **Testing video folders**: {len(test_dirs)}
- **GT mask files (.npy)**: {len(masks)}
- **Training frames (jpg/png)**: {train_imgs}
- **Testing frames (jpg/png)**: {test_imgs}

## Next Steps

{'Dataset ready. Run `python main.py` to start the pipeline.' if success else 'Download failed. See DOWNLOAD_INSTRUCTIONS.md for manual steps. Use `scripts/create_sample_shanghaitech.py` for synthetic data.'}
"""
    STATUS_FILE.write_text(content, encoding="utf-8")
    print(f"\nStatus report written to {STATUS_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("ShanghaiTech Campus Dataset Downloader")
    print("=" * 60)

    _ensure_dirs()

    if _dataset_looks_complete():
        print("Dataset already present — skipping download.")
        _write_status(success=True, method="already_present")
        return

    success = False
    method = "none"

    # ----- Strategy A: Google Drive folders -----
    print("\n[Strategy A] Google Drive folder download…")
    ok_train = _try_gdrive_folder(GDRIVE_TRAIN_FOLDER, TRAINING_FRAMES, "training")
    ok_test = _try_gdrive_folder(GDRIVE_TEST_FOLDER, TESTING_FRAMES.parent, "testing")
    if ok_train and ok_test:
        success = True
        method = "gdrive_folder"
    elif ok_train:
        success = True
        method = "gdrive_folder_train_only"
    elif ok_test:
        success = True
        method = "gdrive_folder_test_only"

    # ----- Strategy B: Google Drive file IDs -----
    if not success:
        print("\n[Strategy B] Google Drive file IDs…")
        for fid in CANDIDATE_TRAIN_IDS:
            if _try_gdrive_file(fid, TRAINING_FRAMES, "training"):
                success = True
                method = "gdrive_file_train"
                break
        for fid in CANDIDATE_TEST_IDS:
            if _try_gdrive_file(fid, TESTING_FRAMES.parent, "testing"):
                success = True
                method = method + "+gdrive_file_test" if success else "gdrive_file_test"
                break

    # ----- Strategy C: Kaggle -----
    if not success:
        print("\n[Strategy C] Kaggle API…")
        if _try_kaggle(DEST):
            success = True
            method = "kaggle"

    # ----- Fallback -----
    if not success:
        print("\n[Fallback] All automatic methods failed.")
        _write_instructions()

    _write_status(success=success, method=method)

    if success:
        print("\nDownload complete!")
    else:
        print("\nAutomatic download failed.")
        print(f"See {INSTRUCTIONS_FILE} for manual instructions.")
        print("Run `scripts/create_sample_shanghaitech.py` for synthetic test data.")


if __name__ == "__main__":
    main()
