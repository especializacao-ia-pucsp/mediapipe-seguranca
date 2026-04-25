---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# `03_feature_engineering.ipynb`

## Notebook 03 — Feature Engineering (Fase 4)

## Navegação do notebook

- [Início](../README.md)
- [Índice dos notebooks](README.md)
- [Anterior: extração com MediaPipe](02_extracao_mediapipe.md)
- [Próximo: EDA](04_eda.md)
- [Dados processados](../data/processed/README.md)
- [Dicionário de dados](../docs/DICIONARIO_DE_DADOS.md)
- [Validação Fase 4](../reports/eda/fase4_validacao_base_processada.md)
- [Código-fonte](../src/README.md)

## Objetivo

Demonstrar a **base analítica consolidada** da Fase 4 — `frame_features_real` e
`window_features_real` — lendo os parquets já produzidos pelo pipeline
(`python main.py --mode real ...` → `build_processed_base`). Validar schema,
linhagem e qualidade, e visualizar os sinais que servirão de insumo à EDA da Fase 5.

> Este notebook **não regenera** a base. Ele apenas lê os artefatos em
> `data/processed/` e produz figuras em `reports/figures/`.

**Data:** 2026-04-25

## Setup

```python
import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from mediapipe_seguranca.feature_engineering_real import (
    FRAME_FEATURES_SCHEMA,
    WINDOW_FEATURES_SCHEMA,
    PIPELINE_VERSION,
)

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

FRAME_PATH = PROCESSED / "frame_features_real.parquet"
WINDOW_PATH = PROCESSED / "window_features_real.parquet"
QUALITY_PATH = PROCESSED / "data_quality_report.json"

print(f"PROCESSED   = {PROCESSED}")
print(f"FRAME_PATH  = {FRAME_PATH.name}  (exists={FRAME_PATH.exists()})")
print(f"WINDOW_PATH = {WINDOW_PATH.name} (exists={WINDOW_PATH.exists()})")
print(f"QUALITY     = {QUALITY_PATH.name}    (exists={QUALITY_PATH.exists()})")
print(f"PIPELINE_VERSION (código) = {PIPELINE_VERSION}")
```

## Carregar artefatos

```python
df_frames = pd.DataFrame()
df_windows = pd.DataFrame()
quality: dict = {}

if FRAME_PATH.exists():
    df_frames = pd.read_parquet(FRAME_PATH)
if WINDOW_PATH.exists():
    df_windows = pd.read_parquet(WINDOW_PATH)
if QUALITY_PATH.exists():
    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))

print(f"df_frames  shape: {df_frames.shape}")
print(f"df_windows shape: {df_windows.shape}")
```

```python
df_frames.head()
```

```python
df_windows.head()
```

```python
df_frames.dtypes
```

## Validação visual de schema

Confirma que **todas** as colunas declaradas em `FRAME_FEATURES_SCHEMA` /
`WINDOW_FEATURES_SCHEMA` existem nos parquets. Colunas extras são esperadas e
correspondem à **linhagem** (`source_split`, `frame_stride`, `window_size`,
`pipeline_version`, `extraction_timestamp`).

```python
def _check_schema(df: pd.DataFrame, schema: list[str], label: str) -> None:
    cols = set(df.columns)
    missing = [c for c in schema if c not in cols]
    extras = sorted(cols - set(schema))
    print(f"[{label}] schema OK: {not missing}  | faltando: {missing}")
    print(f"[{label}] colunas extras (linhagem): {extras}")

if not df_frames.empty:
    _check_schema(df_frames, FRAME_FEATURES_SCHEMA, "frames")
if not df_windows.empty:
    _check_schema(df_windows, WINDOW_FEATURES_SCHEMA, "windows")
```

## Relatório de qualidade

```python
if quality:
    summary = {
        "pipeline_version": quality.get("pipeline_version"),
        "extraction_timestamp": quality.get("extraction_timestamp"),
        "total_frames": quality.get("total_frames"),
        "total_videos": quality.get("total_videos"),
        "total_windows": quality.get("total_windows"),
        "frames_without_detection": quality.get("frames_without_detection"),
        "frames_with_fallback": quality.get("frames_with_fallback"),
    }
    df_quality = pd.DataFrame(summary.items(), columns=["métrica", "valor"])
    display(df_quality)
```

## Estatísticas descritivas

```python
if not df_frames.empty:
    num_cols = df_frames.select_dtypes(include="number").columns
    display(df_frames[num_cols].describe())
```

```python
if not df_windows.empty:
    num_cols_w = df_windows.select_dtypes(include="number").columns
    display(df_windows[num_cols_w].describe())
```

## Visualizações

### Boxplot — `motion_proxy_norm` por vídeo

```python
if not df_frames.empty:
    fig, ax = plt.subplots(figsize=(7, 4))
    df_frames.boxplot(column="motion_proxy_norm", by="video_id", ax=ax)
    ax.set_title("Fase 4 — motion_proxy_norm por video_id")
    ax.set_xlabel("video_id")
    ax.set_ylabel("motion_proxy_norm")
    plt.suptitle("")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase4_motion_proxy_norm_por_video.png", dpi=120)
    plt.show()
```

### Linha — `motion_proxy_norm_mean` ao longo das janelas

```python
if not df_windows.empty:
    fig, ax = plt.subplots(figsize=(9, 4))
    for video_id, sub in df_windows.groupby("video_id"):
        ax.plot(sub["window_id"], sub["motion_proxy_norm_mean"],
                marker="o", label=video_id)
    ax.set_title("Fase 4 — motion_proxy_norm_mean por window_id")
    ax.set_xlabel("window_id")
    ax.set_ylabel("motion_proxy_norm_mean")
    ax.legend(title="video_id")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase4_window_motion_timeline.png", dpi=120)
    plt.show()
```

### Histograma — `num_people_detected`

> **Limitação herdada do SAMPLE:** os vídeos atuais do ShanghaiTech SAMPLE têm pessoas
> pequenas/distantes que ficam abaixo do `min_pose_detection_confidence` do
> `pose_landmarker_lite`. Por isso `num_people_detected` é **0 em todos os frames**, e
> sinais derivados de pose (`mean_pose_visibility`, `bbox_area_*`, `pose_quality`) ficam
> nulos. Não é falha de feature engineering — é característica do conteúdo + modelo lite.
> A Fase 5 só será conclusiva sobre o dataset real expandido.

```python
if not df_frames.empty:
    fig, ax = plt.subplots(figsize=(7, 4))
    max_people = int(df_frames["num_people_detected"].max())
    df_frames["num_people_detected"].plot.hist(
        bins=range(0, max(max_people + 2, 3)),
        ax=ax, edgecolor="black", color="#4C72B0",
    )
    ax.set_title("Fase 4 — Distribuição de num_people_detected (SAMPLE)")
    ax.set_xlabel("num_people_detected")
    ax.set_ylabel("frames")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase4_distribuicao_num_people.png", dpi=120)
    plt.show()
```

### Resumo de qualidade — barras horizontais

```python
if quality:
    metrics = {
        "frames_without_detection": quality.get("frames_without_detection", 0),
        "frames_with_fallback": quality.get("frames_with_fallback", 0),
        "total_frames": quality.get("total_frames", 0),
    }
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(list(metrics.keys()), list(metrics.values()),
            color=["#DD8452", "#8172B3", "#4C72B0"])
    ax.set_title("Fase 4 — Resumo do data_quality_report")
    ax.set_xlabel("frames")
    for i, v in enumerate(metrics.values()):
        ax.text(v, i, f" {v}", va="center")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase4_quality_summary.png", dpi=120)
    plt.show()
```

## Linhagem e versão

Confirma a rastreabilidade da base: cada linha carrega de qual extração veio.

```python
if not df_frames.empty:
    print("--- frames ---")
    for col in ("pipeline_version", "extraction_timestamp", "window_size",
                "frame_stride", "source_split"):
        if col in df_frames.columns:
            print(f"  {col}: {sorted(df_frames[col].dropna().unique().tolist())}")

if not df_windows.empty:
    print("--- windows ---")
    for col in ("pipeline_version", "extraction_timestamp", "window_size"):
        if col in df_windows.columns:
            print(f"  {col}: {sorted(df_windows[col].dropna().unique().tolist())}")
```

## Achados e próximos passos

- **PASS** — base analítica consolidada disponível em `data/processed/` (parquet + csv),
  com schema versionado (`FRAME_FEATURES_SCHEMA`, `WINDOW_FEATURES_SCHEMA`) e linhagem
  carregada em cada linha (`pipeline_version`, `extraction_timestamp`, `window_size`,
  `frame_stride`, `source_split`).
- **Limitação observada** — o SAMPLE atual produz `num_people_detected=0` em todos os
  frames; sinais de pose ficam nulos e a variabilidade analítica vem essencialmente do
  `motion_proxy_norm`. A base é **estruturalmente correta**, mas com baixa riqueza
  semântica até que o ShanghaiTech expandido seja processado.
- **Próximo passo (Fase 5)** — EDA estatística sobre essa base (distribuições, correlações,
  estabilidade entre vídeos) usando o notebook [04_eda.md](04_eda.md), e atualização das
  conclusões assim que o dataset real expandido estiver disponível.
