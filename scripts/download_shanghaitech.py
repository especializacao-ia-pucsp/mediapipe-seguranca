"""
Download ShanghaiTech Campus Dataset for anomaly detection.

Tries multiple sources in order:
    A) Official public OneDrive share
    B) Google Drive folder download via gdown
    C) Google Drive file IDs (tar archives) via gdown
    D) Kaggle API (if configured)
    E) Graceful fallback with manual instructions + SAMPLE auto-generation
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request
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
# Option A - official OneDrive public share
ONEDRIVE_SHARE_URL = "https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y"

# Option B - Google Drive folders (pre-extracted frames shared by researchers)
GDRIVE_TRAIN_FOLDER = "https://drive.google.com/drive/folders/1fPOb0vH7Vy9L4RhSivniQlmxhKa3JXIL"
GDRIVE_TEST_FOLDER = "https://drive.google.com/drive/folders/1njFiC9bO6-A_0AxKQpZKHfF3xUPDiXzc"

# Option C - single archive file IDs
CANDIDATE_TRAIN_IDS: list[str] = [
    "1rymF0gLYjb9K9h0q5BXc3iHMOGMXRnuD",
    "1bN6YV3bpv1wFuPlDR1xh_-P1Ge-B-Ywk",
]
CANDIDATE_TEST_IDS: list[str] = [
    "1UlIjUScPnjijBDHE0LYrXaVAY9v7yLaG",
    "1CbkaqeRK0yEI2I9hMJH4G0CXHV8mvhkJ",
]

# Option D - Kaggle (dataset slug)
KAGGLE_DATASET = "defeatthefake/shanghaitech-campus-dataset"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RELEVANT_ARCHIVE_EXTENSIONS = (".tar", ".tar.gz", ".tgz", ".zip")
NPY_GLOB = "*.npy"
DOWNLOADER_USER_AGENT = "mediapipe-seguranca-downloader/1.0"


def _ensure_dirs() -> None:
    for d in [TRAINING_FRAMES, TESTING_FRAMES, TESTING_MASKS]:
        d.mkdir(parents=True, exist_ok=True)


def _count_images(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.rglob("*.jpg")) + sum(1 for _ in directory.rglob("*.png"))


def _count_masks(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.glob(NPY_GLOB))


def _dataset_counts() -> tuple[int, int, int]:
    train_dirs = [p for p in TRAINING_FRAMES.iterdir() if p.is_dir()] if TRAINING_FRAMES.exists() else []
    test_dirs = [p for p in TESTING_FRAMES.iterdir() if p.is_dir()] if TESTING_FRAMES.exists() else []
    masks = list(TESTING_MASKS.glob(NPY_GLOB)) if TESTING_MASKS.exists() else []
    return len(train_dirs), len(test_dirs), len(masks)


def _real_dataset_minimum_ready() -> bool:
    """Operational minimum: train dirs >= 1, test dirs >= 1, masks >= 1."""
    train_count, test_count, mask_count = _dataset_counts()
    return train_count >= 1 and test_count >= 1 and mask_count >= 1


def _real_dataset_complete() -> bool:
    """Complete dataset: train dirs >= 300, test dirs >= 100, masks >= 100."""
    train_count, test_count, mask_count = _dataset_counts()
    return train_count >= 300 and test_count >= 100 and mask_count >= 100


def _real_dataset_status_label() -> str:
    """Return complete/partial/absent based on observed real dataset structure."""
    train_count, test_count, mask_count = _dataset_counts()
    if train_count == 0 and test_count == 0 and mask_count == 0:
        return "absent"
    if train_count >= 300 and test_count >= 100 and mask_count >= 100:
        return "complete"
    return "partial"


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


def _path_tail_equals(path: Path, tail_parts: tuple[str, ...]) -> bool:
    if len(path.parts) < len(tail_parts):
        return False
    path_tail = [p.lower() for p in path.parts[-len(tail_parts) :]]
    return path_tail == [p.lower() for p in tail_parts]


def _move_path_if_absent(item: Path, target: Path) -> int:
    if target.exists():
        return 0
    shutil.move(str(item), str(target))
    return 1


def _merge_nested_directory(item: Path, target: Path) -> int:
    moved = _merge_dir_contents(item, target)
    if item.exists() and not any(item.iterdir()):
        item.rmdir()
    return moved


def _merge_item_into_target(item: Path, target: Path) -> int:
    if item.is_dir() and target.exists() and target.is_dir():
        return _merge_nested_directory(item, target)
    return _move_path_if_absent(item, target)


def _merge_dir_contents(src: Path, dest: Path) -> int:
    """Move files/subdirectories from src into dest and return moved item count."""
    moved = 0
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dest / item.name
        moved += _merge_item_into_target(item, target)
    return moved


def _find_dirs_matching_tail(root: Path, tail_parts: tuple[str, ...]) -> list[Path]:
    if not root.exists():
        return []
    matches: list[Path] = []
    for candidate in root.rglob("*"):
        if not candidate.is_dir():
            continue
        # Never normalize from SAMPLE or temporary download folders.
        if "SAMPLE" in candidate.parts or "_downloads_onedrive" in candidate.parts:
            continue
        if _path_tail_equals(candidate, tail_parts):
            matches.append(candidate)
    return matches


def _normalize_tail_to_dest(root: Path, tail_parts: tuple[str, ...], dest: Path) -> int:
    moved = 0
    for candidate in _find_dirs_matching_tail(root, tail_parts):
        if candidate.resolve() == dest.resolve():
            continue
        moved += _merge_dir_contents(candidate, dest)
    return moved


def _move_subdirs_to_frames(parent_dir: Path, frames_dir: Path, reserved_names: set[str]) -> int:
    moved = 0
    if parent_dir.resolve() != frames_dir.parent.resolve():
        return moved

    for child in parent_dir.iterdir():
        if child.is_dir() and child.name not in reserved_names:
            target = frames_dir / child.name
            if not target.exists():
                shutil.move(str(child), str(target))
                moved += 1
    return moved


def _normalize_top_level_dirs(
    root: Path, parent_tail: tuple[str, ...], frames_dir: Path, reserved_names: set[str]
) -> int:
    moved = 0
    for parent_dir in _find_dirs_matching_tail(root, parent_tail):
        moved += _move_subdirs_to_frames(parent_dir, frames_dir, reserved_names)
    return moved


def _normalize_dataset_layout() -> None:
    """Normalize extracted data into training/frames, testing/frames, testing/test_frame_mask."""
    moved_total = 0
    moved_total += _normalize_tail_to_dest(DEST, ("training", "frames"), TRAINING_FRAMES)
    moved_total += _normalize_tail_to_dest(DEST, ("testing", "frames"), TESTING_FRAMES)
    moved_total += _normalize_tail_to_dest(DEST, ("testing", "test_frame_mask"), TESTING_MASKS)
    moved_total += _normalize_top_level_dirs(DEST, ("training",), TRAINING_FRAMES, {"frames"})
    moved_total += _normalize_top_level_dirs(DEST, ("testing",), TESTING_FRAMES, {"frames", "test_frame_mask"})

    if moved_total > 0:
        print(f"  Normalized extracted layout ({moved_total} items moved)")


def _gdown_available() -> bool:
    try:
        import gdown  # noqa: F401

        return True
    except ImportError:
        return False


def _build_request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": DOWNLOADER_USER_AGENT})


def _http_get_json(url: str, timeout: int = 60) -> dict | None:
    request = _build_request(url)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
            data = json.loads(payload)
            if isinstance(data, dict):
                return data
            return None
    except Exception:
        return None


def _resolve_short_url(url: str) -> str | None:
    """Resolve URL redirects and return final URL."""
    request = _build_request(url)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.geturl()
    except Exception:
        return None


def _to_share_token(url: str) -> str:
    raw = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
    return f"u!{raw}"


def _is_archive_candidate(name: str) -> bool:
    lower = name.lower()
    if not lower.endswith(RELEVANT_ARCHIVE_EXTENSIONS):
        return False
    keywords = ("train", "test", "shanghai", "campus", "dataset")
    return any(key in lower for key in keywords)


def _download_file(url: str, output_path: Path) -> bool:
    request = _build_request(url)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("wb") as f:
                shutil.copyfileobj(response, f)
        if output_path.stat().st_size < 1024:
            print(f"  Downloaded file is too small: {output_path.name}")
            output_path.unlink(missing_ok=True)
            return False
        return True
    except Exception as exc:
        print(f"  Download failed for {output_path.name}: {exc}")
        output_path.unlink(missing_ok=True)
        return False


def _fetch_onedrive_driveitem(share_token: str) -> tuple[dict, str] | None:
    token_q = urllib.parse.quote(share_token, safe="!")
    api_bases = ["https://api.onedrive.com/v1.0", "https://graph.microsoft.com/v1.0"]
    for base in api_bases:
        url = f"{base}/shares/{token_q}/driveItem"
        data = _http_get_json(url)
        if data is not None:
            return data, base
    return None


def _onedrive_payload_items(payload: dict | None) -> list[dict]:
    if not isinstance(payload, dict):
        return []
    value = payload.get("value", [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _onedrive_next_link(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return ""
    next_candidate = payload.get("@odata.nextLink")
    return next_candidate if isinstance(next_candidate, str) else ""


def _iter_onedrive_children(share_token: str, api_base: str) -> list[dict]:
    token_q = urllib.parse.quote(share_token, safe="!")
    next_url = f"{api_base}/shares/{token_q}/driveItem/children?$top=200"
    items: list[dict] = []

    while next_url:
        payload = _http_get_json(next_url)
        if payload is None:
            break

        items.extend(_onedrive_payload_items(payload))
        next_url = _onedrive_next_link(payload)

    return items


def _list_onedrive_archives_from_folder(share_token: str, api_base: str) -> list[dict]:
    archives: list[dict] = []
    for item in _iter_onedrive_children(share_token, api_base):
        name = str(item.get("name", ""))
        if _is_archive_candidate(name):
            archives.append(item)
    return archives


def _candidate_onedrive_urls(url: str) -> list[str]:
    final_url = _resolve_short_url(url)
    if final_url:
        print(f"  Resolved OneDrive URL: {final_url}")
    else:
        print("  Could not resolve short URL; trying original URL token")

    candidate_urls: list[str] = [url]
    if final_url and final_url not in candidate_urls:
        candidate_urls.insert(0, final_url)
    return candidate_urls


def _collect_archives_from_driveitem(driveitem: dict, api_base: str, share_token: str) -> list[tuple[str, str]]:
    archives: list[tuple[str, str]] = []
    if "folder" in driveitem:
        print("  OneDrive share appears to be a folder; listing children")
        for item in _list_onedrive_archives_from_folder(share_token, api_base):
            name = str(item.get("name", "download.bin"))
            download_url = item.get("@microsoft.graph.downloadUrl")
            if isinstance(download_url, str):
                archives.append((name, download_url))
        return archives

    name = str(driveitem.get("name", "download.bin"))
    download_url = driveitem.get("@microsoft.graph.downloadUrl")
    if isinstance(download_url, str) and _is_archive_candidate(name):
        print("  OneDrive share appears to be a file")
        archives.append((name, download_url))
    return archives


def _find_onedrive_archives(candidate_urls: list[str]) -> list[tuple[str, str]]:
    for source_url in candidate_urls:
        share_token = _to_share_token(source_url)
        driveitem_payload = _fetch_onedrive_driveitem(share_token)
        if driveitem_payload is None:
            continue

        driveitem, api_base = driveitem_payload
        archives = _collect_archives_from_driveitem(driveitem, api_base, share_token)
        if archives:
            return archives
    return []


def _download_onedrive_archives(archives_to_download: list[tuple[str, str]], dest: Path) -> list[Path]:
    download_dir = dest / "_downloads_onedrive"
    download_dir.mkdir(parents=True, exist_ok=True)
    downloaded_archives: list[Path] = []

    for name, download_url in archives_to_download:
        output_path = download_dir / name
        print(f"  Downloading from OneDrive: {name}")
        if _download_file(download_url, output_path):
            downloaded_archives.append(output_path)
    return downloaded_archives


def _extract_archives_to_dest(archives: list[Path], dest: Path) -> bool:
    extracted_any = False
    for archive_path in archives:
        extracted_any = _extract_archive(archive_path, dest) or extracted_any
    return extracted_any


def _try_onedrive_share(url: str, dest: Path) -> bool:
    print(f"  Trying official OneDrive share: {url}")

    candidate_urls = _candidate_onedrive_urls(url)
    archives_to_download = _find_onedrive_archives(candidate_urls)

    if not archives_to_download:
        print("  OneDrive API did not return downloadable archive files")
        return False

    downloaded_archives = _download_onedrive_archives(archives_to_download, dest)

    if not downloaded_archives:
        print("  OneDrive download did not retrieve usable archives")
        return False

    extracted_any = _extract_archives_to_dest(downloaded_archives, dest)

    _normalize_dataset_layout()
    return extracted_any and _real_dataset_complete()


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
        _normalize_dataset_layout()
        return _real_dataset_complete()
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
- Official OneDrive share: https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y
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

## Alternatives: Academic Torrents / Roboflow / Kaggle

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


def _write_status(method: str, sample_auto_generated: bool = False) -> None:
    train_dirs = [p for p in TRAINING_FRAMES.iterdir() if p.is_dir()] if TRAINING_FRAMES.exists() else []
    test_dirs = [p for p in TESTING_FRAMES.iterdir() if p.is_dir()] if TESTING_FRAMES.exists() else []
    masks = list(TESTING_MASKS.glob(NPY_GLOB)) if TESTING_MASKS.exists() else []
    train_imgs = _count_images(TRAINING_FRAMES)
    test_imgs = _count_images(TESTING_FRAMES)

    real_complete = _real_dataset_complete()
    real_minimum = _real_dataset_minimum_ready()
    real_state = _real_dataset_status_label()
    sample_root = DEST / "SAMPLE"
    sample_ready = (sample_root / "training" / "frames").exists() and (sample_root / "testing" / "frames").exists()

    if real_complete:
        status = "SUCCESS"
        next_steps = "Real dataset complete. Ready for Fase 3 extraction at scale."
    elif real_minimum or sample_ready:
        status = "PARTIAL_READY"
        next_steps = (
            "Pipeline runnable, but real dataset is incomplete. Re-run with --force-real or complete manual download."
        )
    else:
        status = "FAILED"
        next_steps = (
            "Download failed with no operational dataset. See DOWNLOAD_INSTRUCTIONS.md for manual recovery steps."
        )

    content = f"""# ShanghaiTech Download Status

- **Status**: {status}
- **Real dataset state**: {real_state}
- **Method**: {method}
- **Real dataset complete**: {'yes' if real_complete else 'no'}
- **Real dataset operational minimum**: {'yes' if real_minimum else 'no'}
- **Training video folders**: {len(train_dirs)}
- **Testing video folders**: {len(test_dirs)}
- **GT mask files (.npy)**: {len(masks)}
- **Training frames (jpg/png)**: {train_imgs}
- **Testing frames (jpg/png)**: {test_imgs}
- **SAMPLE generated automatically**: {'yes' if sample_auto_generated else 'no'}
- **SAMPLE available**: {'yes' if sample_ready else 'no'}

## Next Steps

{next_steps}
"""
    STATUS_FILE.write_text(content, encoding="utf-8")
    print(f"\nStatus report written to {STATUS_FILE}")


def _generate_sample_dataset() -> bool:
    sample_script = PROJECT_ROOT / "scripts" / "create_sample_shanghaitech.py"
    print("\nGenerating SAMPLE dataset automatically...")
    try:
        result = subprocess.run([sys.executable, str(sample_script)], capture_output=True, text=True)
        if result.returncode != 0:
            print("  SAMPLE generation failed")
            print(result.stderr[:500])
            return False
        print("  SAMPLE dataset generated successfully")
        return True
    except Exception as exc:
        print(f"  SAMPLE generation error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download ShanghaiTech dataset with fallback options")
    parser.add_argument(
        "--force-real",
        action="store_true",
        help="Force real dataset download attempts even when complete/partial structure already exists.",
    )
    parser.add_argument(
        "--skip-sample",
        action="store_true",
        help="Do not auto-generate SAMPLE dataset in fallback.",
    )
    return parser.parse_args()


def _run_strategy_onedrive() -> tuple[bool, str]:
    print("\n[Strategy A] Official OneDrive share...")
    success = _try_onedrive_share(ONEDRIVE_SHARE_URL, DEST) and _real_dataset_complete()
    return success, "onedrive_share" if success else "none"


def _run_strategy_gdrive_folders() -> tuple[bool, str]:
    print("\n[Strategy B] Google Drive folder download...")
    _try_gdrive_folder(GDRIVE_TRAIN_FOLDER, TRAINING_FRAMES, "training")
    _try_gdrive_folder(GDRIVE_TEST_FOLDER, TESTING_FRAMES.parent, "testing")
    _normalize_dataset_layout()
    success = _real_dataset_complete()
    return success, "gdrive_folder" if success else "none"


def _try_first_gdrive_file(ids: list[str], dest_dir: Path, label: str) -> bool:
    for fid in ids:
        if _try_gdrive_file(fid, dest_dir, label):
            return True
    return False


def _run_strategy_gdrive_files() -> tuple[bool, str]:
    print("\n[Strategy C] Google Drive file IDs...")
    downloaded_any = False
    downloaded_any = _try_first_gdrive_file(CANDIDATE_TRAIN_IDS, TRAINING_FRAMES, "training") or downloaded_any
    downloaded_any = _try_first_gdrive_file(CANDIDATE_TEST_IDS, TESTING_FRAMES.parent, "testing") or downloaded_any

    if downloaded_any:
        _normalize_dataset_layout()
    success = downloaded_any and _real_dataset_complete()
    return success, "gdrive_file" if success else "none"


def _run_strategy_kaggle() -> tuple[bool, str]:
    print("\n[Strategy D] Kaggle API...")
    if not _try_kaggle(DEST):
        return False, "none"
    _normalize_dataset_layout()
    success = _real_dataset_complete()
    return success, "kaggle" if success else "none"


def _run_fallback(skip_sample: bool) -> bool:
    print("\n[Fallback] Real dataset download did not reach minimum operational structure.")
    _write_instructions()
    if skip_sample:
        print("  --skip-sample enabled: skipping SAMPLE auto-generation.")
        return False
    return _generate_sample_dataset()


def main() -> None:
    args = _parse_args()

    print("=" * 60)
    print("ShanghaiTech Campus Dataset Downloader")
    print("=" * 60)

    _ensure_dirs()
    _normalize_dataset_layout()

    if _real_dataset_complete() and not args.force_real:
        print("Real dataset already complete — skipping download.")
        _write_status(method="already_complete")
        return

    if args.force_real:
        print("--force-real enabled: attempting all real download strategies.")
    elif _real_dataset_status_label() == "partial":
        print("Partial real dataset detected — continuing download strategies to complete it.")

    success = False
    method = "none"
    sample_auto_generated = False

    strategies = [
        _run_strategy_onedrive,
        _run_strategy_gdrive_folders,
        _run_strategy_gdrive_files,
        _run_strategy_kaggle,
    ]

    for strategy in strategies:
        if success:
            break
        success, method = strategy()

    if not success:
        sample_auto_generated = _run_fallback(args.skip_sample)

    _write_status(method=method, sample_auto_generated=sample_auto_generated)

    if success:
        print("\nReal dataset download complete and operationally ready.")
    else:
        print("\nAutomatic real dataset download not completed.")
        print(f"See {INSTRUCTIONS_FILE} for manual instructions.")
        if sample_auto_generated:
            print("SAMPLE dataset was generated automatically for immediate pipeline usage.")
        else:
            print("Run `scripts/create_sample_shanghaitech.py` for synthetic test data.")


if __name__ == "__main__":
    main()
