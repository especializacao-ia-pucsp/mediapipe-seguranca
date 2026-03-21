from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data_raw: Path
    data_interim: Path
    data_processed: Path
    data_labels: Path
    reports: Path


def get_project_paths(root: Path | None = None) -> ProjectPaths:
    project_root = root or Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    return ProjectPaths(
        root=project_root,
        data_raw=data_dir / "raw",
        data_interim=data_dir / "interim",
        data_processed=data_dir / "processed",
        data_labels=data_dir / "labels",
        reports=project_root / "reports",
    )
