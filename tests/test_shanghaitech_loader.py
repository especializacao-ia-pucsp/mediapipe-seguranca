from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mediapipe_seguranca import shanghaitech_loader  # noqa: E402


class ShanghaiTechLoaderResolveRootTests(unittest.TestCase):
    def test_prefers_sample_when_real_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            real_train = temp_root / "training" / "frames" / "01_001"
            sample_train = temp_root / "SAMPLE" / "training" / "frames" / "01_001"
            sample_test = temp_root / "SAMPLE" / "testing" / "frames" / "01_0001"
            sample_masks = temp_root / "SAMPLE" / "testing" / "test_frame_mask"

            real_train.mkdir(parents=True, exist_ok=True)
            sample_train.mkdir(parents=True, exist_ok=True)
            sample_test.mkdir(parents=True, exist_ok=True)
            sample_masks.mkdir(parents=True, exist_ok=True)
            (sample_masks / "01_0001.npy").write_bytes(b"x")

            with patch("mediapipe_seguranca.shanghaitech_loader._shanghaitech_root", return_value=temp_root):
                resolved = shanghaitech_loader._resolve_dataset_root()

            self.assertEqual(resolved, temp_root / "SAMPLE")

    def test_prefers_real_when_minimum_structure_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "training" / "frames" / "01_001").mkdir(parents=True, exist_ok=True)
            (temp_root / "testing" / "frames" / "01_0001").mkdir(parents=True, exist_ok=True)
            masks_dir = temp_root / "testing" / "test_frame_mask"
            masks_dir.mkdir(parents=True, exist_ok=True)
            (masks_dir / "01_0001.npy").write_bytes(b"x")

            with patch("mediapipe_seguranca.shanghaitech_loader._shanghaitech_root", return_value=temp_root):
                resolved = shanghaitech_loader._resolve_dataset_root()

            self.assertEqual(resolved, temp_root)


if __name__ == "__main__":
    unittest.main()
