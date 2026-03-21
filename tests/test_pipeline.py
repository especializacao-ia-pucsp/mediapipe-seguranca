from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mediapipe_seguranca.pipeline import run_demo_pipeline


class PipelineTests(unittest.TestCase):
    def test_demo_pipeline_creates_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "demo.csv"
            result = run_demo_pipeline(output_path=output_path)

            self.assertTrue(output_path.exists())
            self.assertGreater(result["rows"], 0)
            self.assertIn("normal", result["labels"])
            self.assertIn("evento_risco", result["labels"])


if __name__ == "__main__":
    unittest.main()