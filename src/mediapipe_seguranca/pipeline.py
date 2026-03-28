from __future__ import annotations

import argparse
from pathlib import Path

from .config import get_project_paths
from .feature_engineering import aggregate_window_features
from .mediapipe_extract import generate_demo_observations
from .tracking_features import enrich_frame_features
from .train_supervised import run_supervised_baseline
from .train_unsupervised import run_unsupervised_baseline
from .video_io import build_synthetic_frame_metadata


def run_demo_pipeline(output_path: Path | None = None) -> dict[str, object]:
    paths = get_project_paths()
    frame_metadata = build_synthetic_frame_metadata(total_frames=180, window_size=15)
    frame_observations = generate_demo_observations(frame_metadata)
    frame_features = enrich_frame_features(frame_observations)
    window_features = aggregate_window_features(frame_features)
    unsupervised_output = run_unsupervised_baseline(window_features)
    supervised_output = run_supervised_baseline(window_features)

    destination = output_path or paths.data_processed / "demo_window_features.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    unsupervised_output.to_csv(destination, index=False)

    return {
        "rows": len(unsupervised_output),
        "columns": unsupervised_output.columns.tolist(),
        "output_path": str(destination),
        "labels": window_features["label"].value_counts().to_dict(),
        "supervised_accuracy": supervised_output["metrics"]["accuracy"],
    }


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline inicial do projeto MediaPipe Segurança.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho opcional para salvar o CSV de features por janela.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    result = run_demo_pipeline(output_path=args.output)

    print("Pipeline demo executada com sucesso.")
    print(f"- janelas processadas: {result['rows']}")
    print(f"- distribuição de rótulos: {result['labels']}")
    print(f"- acurácia supervisionada (baseline): {result['supervised_accuracy']:.3f}")
    print(f"- arquivo gerado: {result['output_path']}")
    return 0
