from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .build_processed_base import build_processed_base
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
    """DEPRECATED (Fase 4): adaptador heurístico mantido para compatibilidade.

    Substituído por :mod:`feature_engineering_real`. Não é mais usado pelo
    `run_real_pipeline`; permanece apenas como referência/legado.
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
    """Run extraction + Fase 4 processed base using real ShanghaiTech frames."""
    from .extract_runner import run_extraction  # local import (mediapipe heavy)

    paths = get_project_paths()
    manifest = run_extraction(
        split=split,
        frame_stride=frame_stride,
        limit_videos=limit_videos,
    )

    splits: tuple[str, ...]
    if split == "both":
        splits = ("training", "testing")
    else:
        splits = (split,)

    summary = build_processed_base(
        interim_dir=paths.interim_mediapipe_frames,
        output_dir=paths.data_processed,
        window_size=window_size,
        splits=splits,
    )

    # If a custom output_path was provided, also write window features there.
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pd.read_parquet(summary["window_features_path"]).to_csv(output_path, index=False)
        summary["window_features_path"] = str(output_path)

    return {
        "rows": int(summary["windows"]),
        "videos": int(manifest["video_id"].nunique()) if not manifest.empty else int(summary["videos"]),
        "frames": int(summary["frames"]),
        "output_path": summary["window_features_path"],
        "quality_report_path": summary["quality_report_path"],
    }


def run_processed_base_pipeline(
    window_size: int = 15,
    splits: tuple[str, ...] = ("training", "testing"),
) -> dict[str, object]:
    """Re-build the processed base from existing interim parquets (no extraction)."""
    paths = get_project_paths()
    return build_processed_base(
        interim_dir=paths.interim_mediapipe_frames,
        output_dir=paths.data_processed,
        window_size=window_size,
        splits=splits,
    )


def run_pipeline(
    mode: str = "demo",
    split: str = "training",
    limit_videos: int | None = None,
    frame_stride: int = 5,
    output_path: Path | None = None,
    window_size: int = 15,
) -> dict[str, object]:
    """Dispatch to the demo, real or processed-base pipeline."""
    if mode == "demo":
        return run_demo_pipeline(output_path=output_path)
    if mode == "real":
        return run_real_pipeline(
            split=split,
            limit_videos=limit_videos,
            frame_stride=frame_stride,
            output_path=output_path,
            window_size=window_size,
        )
    if mode == "processed":
        if split == "both":
            splits: tuple[str, ...] = ("training", "testing")
        elif split in ("training", "testing"):
            splits = (split,)
        else:
            splits = ("training", "testing")
        return run_processed_base_pipeline(window_size=window_size, splits=splits)
    raise ValueError(f"mode inválido: {mode!r} (use 'demo', 'real' ou 'processed')")


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline do projeto MediaPipe Segurança.")
    parser.add_argument(
        "--mode",
        choices=["demo", "real", "processed"],
        default="demo",
        help="Modo de execução: 'demo' (sintético), 'real' (extrai + processa) ou 'processed' (só processa).",
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
    parser.add_argument(
        "--window-size",
        type=int,
        default=15,
        help="Tamanho da janela (frames) para agregação.",
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
        window_size=args.window_size,
    )

    if args.mode == "demo":
        print("Pipeline demo executada com sucesso.")
        print(f"- janelas processadas: {result['rows']}")
        print(f"- distribuição de rótulos: {result['labels']}")
        print(f"- acurácia supervisionada (baseline): {result['supervised_accuracy']:.3f}")
        print(f"- arquivo gerado: {result['output_path']}")
    elif args.mode == "real":
        print("Pipeline real (MediaPipe + ShanghaiTech) executada com sucesso.")
        print(f"- vídeos processados: {result['videos']}")
        print(f"- frames extraídos: {result['frames']}")
        print(f"- janelas: {result['rows']}")
        print(f"- arquivo gerado: {result['output_path']}")
        print(f"- relatório de qualidade: {result['quality_report_path']}")
    else:  # processed
        print("Base processada (Fase 4) gerada com sucesso.")
        print(f"- vídeos: {result['videos']}")
        print(f"- frames: {result['frames']}")
        print(f"- janelas: {result['windows']}")
        print(f"- diretório: {result['output_dir']}")
        print(f"- relatório de qualidade: {result['quality_report_path']}")
    return 0
