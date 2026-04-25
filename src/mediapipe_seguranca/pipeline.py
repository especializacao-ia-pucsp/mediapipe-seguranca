from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

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


def _adapt_real_frames_to_features(frames_df: pd.DataFrame, window_size: int = 15) -> pd.DataFrame:
    """Adapt the real extraction frame schema to the feature_engineering input.

    Maps MediaPipe extraction columns to the loose schema expected by
    :func:`enrich_frame_features` while preserving ``video_id`` and the raw
    extraction columns alongside.
    """
    if frames_df.empty:
        return frames_df

    df = frames_df.copy()
    df["window_id"] = df["frame_index"] // window_size

    motion = df["motion_proxy"].fillna(0.0)
    motion_norm = (motion / motion.max()) if motion.max() > 0 else motion

    adapted = pd.DataFrame(
        {
            "video_id": df["video_id"],
            "frame_index": df["frame_index"].astype(int),
            "window_id": df["window_id"].astype(int),
            "people_count": df["num_people_detected"].astype(int),
            "movement_score": motion_norm.astype(float),
            "posture_change_rate": df["mean_pose_visibility"].fillna(0.0).astype(float),
            "estimated_speed": motion_norm.astype(float),
            "dense_scene": (df["num_people_detected"] >= 4).astype(int),
            "fall_risk_score": (1.0 - df["mean_pose_visibility"].fillna(1.0)).clip(lower=0.0).astype(float),
            "suspicious_loitering": ((df["num_people_detected"] >= 1) & (motion_norm < 0.05)).astype(int),
            "label": "unlabeled",
        }
    )
    return adapted


def run_real_pipeline(
    split: str = "training",
    limit_videos: int | None = None,
    frame_stride: int = 5,
    window_size: int = 15,
    output_path: Path | None = None,
) -> dict[str, object]:
    """Run extraction + feature engineering using real ShanghaiTech frames."""
    from .extract_runner import run_extraction  # local import (mediapipe heavy)

    paths = get_project_paths()
    manifest = run_extraction(
        split=split,
        frame_stride=frame_stride,
        limit_videos=limit_videos,
    )

    frames_root = paths.interim_mediapipe_frames
    parquet_files: list[Path] = []
    for sub in ("training", "testing"):
        sub_dir = frames_root / sub
        if sub_dir.exists():
            parquet_files.extend(sorted(sub_dir.glob("*.parquet")))

    if not parquet_files:
        raise RuntimeError(
            "Nenhum parquet encontrado em data/interim/mediapipe_frames/. "
            "Verifique se o dataset ShanghaiTech está disponível."
        )

    frames_df = pd.concat([pd.read_parquet(p) for p in parquet_files], ignore_index=True)
    adapted = _adapt_real_frames_to_features(frames_df, window_size=window_size)
    enriched = enrich_frame_features(adapted)
    window_features = aggregate_window_features(enriched)

    destination = output_path or paths.data_processed / "window_features_real.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    window_features.to_csv(destination, index=False)

    return {
        "rows": int(len(window_features)),
        "videos": int(manifest["video_id"].nunique()) if not manifest.empty else 0,
        "frames": int(len(frames_df)),
        "output_path": str(destination),
    }


def run_pipeline(
    mode: str = "demo",
    split: str = "training",
    limit_videos: int | None = None,
    frame_stride: int = 5,
    output_path: Path | None = None,
) -> dict[str, object]:
    """Dispatch to the demo or real pipeline."""
    if mode == "demo":
        return run_demo_pipeline(output_path=output_path)
    if mode == "real":
        return run_real_pipeline(
            split=split,
            limit_videos=limit_videos,
            frame_stride=frame_stride,
            output_path=output_path,
        )
    raise ValueError(f"mode inválido: {mode!r} (use 'demo' ou 'real')")


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline do projeto MediaPipe Segurança.")
    parser.add_argument(
        "--mode",
        choices=["demo", "real"],
        default="demo",
        help="Modo de execução: 'demo' (sintético) ou 'real' (MediaPipe + ShanghaiTech).",
    )
    parser.add_argument(
        "--split",
        choices=["training", "testing", "both"],
        default="training",
        help="Split do dataset usado no modo 'real'.",
    )
    parser.add_argument(
        "--limit-videos",
        type=int,
        default=None,
        help="Limita o número de vídeos processados (modo 'real').",
    )
    parser.add_argument(
        "--frame-stride",
        type=int,
        default=5,
        help="Stride de frames no modo 'real' (1 = todos os frames).",
    )
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
    result = run_pipeline(
        mode=args.mode,
        split=args.split,
        limit_videos=args.limit_videos,
        frame_stride=args.frame_stride,
        output_path=args.output,
    )

    if args.mode == "demo":
        print("Pipeline demo executada com sucesso.")
        print(f"- janelas processadas: {result['rows']}")
        print(f"- distribuição de rótulos: {result['labels']}")
        print(f"- acurácia supervisionada (baseline): {result['supervised_accuracy']:.3f}")
        print(f"- arquivo gerado: {result['output_path']}")
    else:
        print("Pipeline real (MediaPipe + ShanghaiTech) executada com sucesso.")
        print(f"- vídeos processados: {result['videos']}")
        print(f"- frames extraídos: {result['frames']}")
        print(f"- janelas: {result['rows']}")
        print(f"- arquivo gerado: {result['output_path']}")
    return 0
