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

# `02_extracao_mediapipe.ipynb`

## Navegação do notebook

- [Início](../README.md)
- [Índice dos notebooks](README.md)
- [Anterior: ingestão](01_ingestao.md)
- [Próximo: feature engineering](03_feature_engineering.md)
- [Dados intermediários](../data/interim/README.md)
- [Arquitetura](../docs/ARQUITETURA.md)
- [Dicionário de dados](../docs/DICIONARIO_DE_DADOS.md)
- [Validação Fase 3](../reports/eda/fase3_validacao_mediapipe.md)

## Objetivo (Fase 3)

Demonstrar a **extração real** com MediaPipe sobre o SAMPLE do ShanghaiTech, validando o
schema dos parquets de frame, o manifesto por vídeo e os sinais derivados (presença de
pessoas, visibilidade média de pose, proxy de movimento e uso do detector como fallback).

> Este notebook **não executa** o MediaPipe — ele apenas lê os artefatos já produzidos
> pelo runner (`python main.py --mode real --split training --limit-videos 2 --frame-stride 5`).

**Data:** 2026-04-25

## Setup

```python
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Raiz do projeto (notebook fica em notebooks/, então sobe um nível)
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
INTERIM_DIR = PROJECT_ROOT / "data" / "interim" / "mediapipe_frames"
TRAINING_DIR = INTERIM_DIR / "training"
MANIFEST_PATH = INTERIM_DIR / "_manifest.parquet"

FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print(f"PROJECT_ROOT  = {PROJECT_ROOT}")
print(f"TRAINING_DIR  = {TRAINING_DIR}  (exists={TRAINING_DIR.exists()})")
print(f"MANIFEST_PATH = {MANIFEST_PATH} (exists={MANIFEST_PATH.exists()})")
print(f"FIGURES_DIR   = {FIGURES_DIR}")
```

## Carregamento dos parquets de frame

Cada vídeo gera um `<video_id>.parquet` em `data/interim/mediapipe_frames/<split>/`.
Concatenamos todos em um único `df_frames`.

```python
df_frames = pd.DataFrame()

if TRAINING_DIR.exists():
    parquet_files = sorted(p for p in TRAINING_DIR.glob("*.parquet") if p.name != "_manifest.parquet")
    print(f"Arquivos encontrados: {len(parquet_files)}")
    for p in parquet_files:
        print(f"  - {p.name} ({p.stat().st_size} bytes)")

    if parquet_files:
        df_frames = pd.concat([pd.read_parquet(p) for p in parquet_files], ignore_index=True)

print(f"\nShape: {df_frames.shape}")
df_frames.head()
```

```python
df_frames.dtypes
```

## Manifesto por vídeo

O manifesto resume cada vídeo processado e é o atalho para diagnóstico rápido (versão do
MediaPipe, frames in/processados, tempo, presença de máscara GT, média de pessoas).

```python
df_manifest = pd.DataFrame()
if MANIFEST_PATH.exists():
    df_manifest = pd.read_parquet(MANIFEST_PATH)
    print(f"Linhas: {len(df_manifest)}")
df_manifest
```

## Estatísticas descritivas

```python
if not df_frames.empty:
    display(df_frames.describe(include="number"))
```

```python
if not df_frames.empty:
    print("Vídeos distintos:", df_frames["video_id"].nunique())
    print("Frames por vídeo:")
    print(df_frames.groupby("video_id")["frame_index"].count())
```

## Visualizações

Todas as figuras são salvas em `reports/figures/` com prefixo `fase3_`.

### Distribuição de `num_people_detected`

> **Achado esperado no SAMPLE/training:** o histograma deve ser dominado por `0`.
> Os vídeos do SAMPLE têm cenas amplas com pessoas pequenas/distantes, que ficam abaixo do
> `min_pose_detection_confidence` padrão do `pose_landmarker_lite`. Não é falha de
> implementação — é característica do conteúdo + modelo lite.

```python
if not df_frames.empty:
    fig, ax = plt.subplots(figsize=(7, 4))
    max_people = int(df_frames["num_people_detected"].max())
    df_frames["num_people_detected"].plot.hist(
        bins=range(0, max_people + 2), ax=ax, edgecolor="black", color="#4C72B0"
    )
    ax.set_title("Fase 3 — Distribuição de num_people_detected (SAMPLE/training)")
    ax.set_xlabel("num_people_detected")
    ax.set_ylabel("frames")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase3_hist_num_people.png", dpi=120)
    plt.show()
```

### Série temporal de `motion_proxy`

Proxy de movimento por diferença média absoluta entre frames consecutivos. Não depende de
detecção de pessoas, então deve estar populado em todos os frames a partir do segundo.

```python
if not df_frames.empty:
    fig, ax = plt.subplots(figsize=(9, 4))
    for video_id, sub in df_frames.groupby("video_id"):
        ax.plot(sub["frame_index"], sub["motion_proxy"], marker="o", label=video_id)
    ax.set_title("Fase 3 — motion_proxy por frame")
    ax.set_xlabel("frame_index")
    ax.set_ylabel("motion_proxy")
    ax.legend(title="video_id")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase3_motion_proxy.png", dpi=120)
    plt.show()
```

### Série temporal de `mean_pose_visibility`

Média de visibilidade dos landmarks de pose. Quando não há detecção, o valor é `NaN` e a
linha simplesmente desaparece — visualmente confirma o achado da seção anterior.

```python
if not df_frames.empty:
    fig, ax = plt.subplots(figsize=(9, 4))
    plotted_any = False
    for video_id, sub in df_frames.groupby("video_id"):
        if sub["mean_pose_visibility"].notna().any():
            ax.plot(sub["frame_index"], sub["mean_pose_visibility"], marker="o", label=video_id)
            plotted_any = True
    if not plotted_any:
        ax.text(
            0.5, 0.5,
            "Sem detecções de pose no SAMPLE/training\n(mean_pose_visibility é NaN em todos os frames)",
            ha="center", va="center", transform=ax.transAxes, fontsize=11, color="#555",
        )
    ax.set_title("Fase 3 — mean_pose_visibility por frame")
    ax.set_xlabel("frame_index")
    ax.set_ylabel("mean_pose_visibility")
    if plotted_any:
        ax.legend(title="video_id")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase3_mean_pose_visibility.png", dpi=120)
    plt.show()
```

### Uso de `detector_fallback_used` por vídeo

Indica em quantos frames o Object Detector (EfficientDet Lite0) foi acionado como fallback
para estimar presença/área de pessoas quando o Pose Landmarker não detectou ninguém.

```python
if not df_frames.empty:
    counts = (
        df_frames.assign(fallback=df_frames["detector_fallback_used"].astype(bool))
        .groupby(["video_id", "fallback"]).size().unstack(fill_value=0)
    )
    # Garante colunas True/False mesmo se uma delas estiver ausente
    for col in (False, True):
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[[False, True]]

    fig, ax = plt.subplots(figsize=(7, 4))
    counts.plot(kind="bar", stacked=True, ax=ax, color=["#4C72B0", "#DD8452"])
    ax.set_title("Fase 3 — detector_fallback_used por vídeo")
    ax.set_xlabel("video_id")
    ax.set_ylabel("frames")
    ax.legend(title="fallback usado", labels=["False", "True"])
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fase3_detector_fallback.png", dpi=120)
    plt.show()
    counts
```

## Justificativa das escolhas técnicas

Conforme [docs/ARQUITETURA.md](../docs/ARQUITETURA.md):

- **Pose Landmarker (lite) como primário** — leve o suficiente para CPU, expõe
  visibilidade por landmark e bbox derivada, suficiente para sinais agregados em janela.
- **Object Detector (EfficientDet Lite0) como fallback** — acionado quando a pose não
  retorna pessoas, garante que `num_people_detected` e `bbox_area_total` ainda capturem
  presença mesmo sem pose válida.
- **`frame_stride=5`** — equilibra custo computacional e resolução temporal para janelas
  curtas; reduz custo de extração em ~5× sem perder estrutura de movimento.
- **Persistência em parquet por vídeo** — schema estável (`FRAME_SCHEMA`), particionamento
  natural por `video_id`, leitura rápida para a fase de feature engineering.

## Achados e próximos passos

**PASS — pipeline real ponta-a-ponta**

- Schema dos parquets de frame estável e idêntico ao `FRAME_SCHEMA`.
- Manifesto consistente, registrando `mediapipe_version`, `processing_seconds`,
  `num_frames_processed`, `mean_people` e `has_gt_mask`.
- Sinais independentes de detecção (`motion_proxy`) populados ao longo dos frames.

**Limitação observada — SAMPLE/training**

- `num_people_detected = 0` em todos os frames processados, com `mean_pose_visibility`
  consequentemente `NaN`. As cenas do SAMPLE têm pessoas pequenas/distantes para o
  `pose_landmarker_lite` em configuração padrão.
- Recomendações para iterações futuras (responsabilidade do Implementador/Operador):
  - executar com `--split testing` (cenas com anomalias e pessoas mais próximas);
  - testar `models/mediapipe/pose_landmarker_full.task`;
  - reduzir `min_pose_detection_confidence` no extrator.

**Próximo passo — Fase 4**

Consolidação da base analítica: agregação por janela usando os parquets de frame como
entrada (`feature_engineering.py`), produzindo `data/processed/window_features_*.csv` com
sinais prontos para EDA (notebook `04_eda.md`) e modelagem (`05_unsupervised.md`,
`06_supervised.md`).
