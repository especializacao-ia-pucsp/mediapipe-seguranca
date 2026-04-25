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

# `04_eda.ipynb`

## Navegação do notebook

- [Início](../README.md)
- [Índice dos notebooks](README.md)
- [Anterior: feature engineering](03_feature_engineering.md)
- [Próximo: não supervisionado](05_unsupervised.md)
- [Dados processados](../data/processed/README.md)
- [Relatórios de EDA](../reports/eda/README.md)
- [Figuras](../reports/figures/README.md)
- [Relatório Fase 5](../reports/eda/fase5_eda_inicial.md)

## Objetivo (Fase 5)

Conduzir análise exploratória estruturada sobre as bases produzidas na Fase 4
(`frame_features_real.parquet`, `window_features_real.parquet`) e contrastar com a base
sintética `demo_window_features.csv`. O foco é:

1. Documentar honestamente o que pode e o que **não pode** ser concluído da base real
   (limitação herdada do SAMPLE do ShanghaiTech).
2. Aprofundar a única dimensão real com sinal: `motion_proxy` e seus derivados.
3. Usar a base DEMO como contraste, demonstrando que o pipeline analítico está pronto
   para receber dados ricos.
4. Produzir insumos para a Fase 6 (modelagem não supervisionada), ainda que parciais.

> Este notebook **não regenera** dados — apenas lê os artefatos já produzidos pelo
> pipeline (`pipeline_version=fase4-v1`).

**Data:** 2026-04-25

## Setup

```python
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    HAS_SNS = True
    sns.set_theme(style="whitegrid")
except ImportError:
    HAS_SNS = False

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
PROCESSED = PROJECT_ROOT / "data" / "processed"
FIG = PROJECT_ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

print(f"PROCESSED = {PROCESSED} (exists={PROCESSED.exists()})")
print(f"FIG       = {FIG}")
print(f"seaborn disponível: {HAS_SNS}")
```

## Carregamento dos artefatos

```python
frames_path = PROCESSED / "frame_features_real.parquet"
windows_path = PROCESSED / "window_features_real.parquet"
demo_path = PROCESSED / "demo_window_features.csv"
quality_path = PROCESSED / "data_quality_report.json"

df_frames = pd.read_parquet(frames_path) if frames_path.exists() else pd.DataFrame()
df_windows = pd.read_parquet(windows_path) if windows_path.exists() else pd.DataFrame()
df_demo = pd.read_csv(demo_path) if demo_path.exists() else pd.DataFrame()
quality = json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else {}

print(f"df_frames  : {df_frames.shape}")
print(f"df_windows : {df_windows.shape}")
print(f"df_demo    : {df_demo.shape}")
print(f"quality keys: {list(quality.keys())}")
```

## Resumo de qualidade da base real

```python
qa_summary = pd.DataFrame({
    "total_frames": [quality.get("total_frames")],
    "total_videos": [quality.get("total_videos")],
    "total_windows": [quality.get("total_windows")],
    "frames_without_detection": [quality.get("frames_without_detection")],
    "frames_with_fallback": [quality.get("frames_with_fallback")],
    "pipeline_version": [quality.get("pipeline_version")],
}).T.rename(columns={0: "valor"})
qa_summary
```

```python
missing = pd.Series(quality.get("missing_per_column", {}), name="n_missing").to_frame()
ranges = pd.DataFrame(quality.get("value_ranges", {})).T
qa_table = ranges.join(missing, how="outer")
qa_table
```

**Limitações herdadas do SAMPLE (3 principais):**

1. `num_people_detected = 0` em **100% dos frames** → todas as features dependentes de
   pose/bbox (`mean_pose_visibility`, `mean_bbox_area`, `pose_quality`,
   `bbox_area_per_person`) são NaN ou zero.
2. Volume insuficiente: apenas **20 frames distribuídos em 2 vídeos** e **8 janelas**
   — qualquer estatística inferencial é meramente descritiva.
3. `detector_fallback_used = False` em todos os registros: o detector também não
   encontrou nada, o que reforça que o problema é o conteúdo do SAMPLE
   (frames esparsos sem pessoas visíveis no recorte testado), não falha do pipeline.

## Estatísticas descritivas

```python
print("=== df_frames.describe() ===")
df_frames.describe(include="all").T
```

```python
print("=== df_windows.describe() ===")
df_windows.describe().T
```

```python
print("=== df_demo.describe() ===")
df_demo.describe().T
```

## Análise focada em `motion_proxy` (REAL)

A única dimensão com sinal real na base atual. Seguem quatro recortes.

### Boxplot de `motion_proxy_norm` por vídeo

```python
fig, ax = plt.subplots(figsize=(7, 4))
videos = sorted(df_frames["video_id"].unique())
data = [df_frames.loc[df_frames["video_id"] == v, "motion_proxy_norm"].values for v in videos]
ax.boxplot(data, labels=videos, showmeans=True)
ax.set_title("motion_proxy_norm por vídeo (REAL)")
ax.set_xlabel("video_id")
ax.set_ylabel("motion_proxy_norm")
fig.tight_layout()
fig.savefig(FIG / "fase5_motion_boxplot_por_video.png", dpi=120)
plt.show()
```

### Linha temporal de `motion_proxy_norm` por frame

```python
fig, ax = plt.subplots(figsize=(9, 4))
for v in videos:
    sub = df_frames[df_frames["video_id"] == v].sort_values("frame_index")
    ax.plot(sub["frame_index"], sub["motion_proxy_norm"], marker="o", label=v)
ax.set_title("motion_proxy_norm ao longo dos frames (REAL)")
ax.set_xlabel("frame_index")
ax.set_ylabel("motion_proxy_norm")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "fase5_motion_timeline_frames.png", dpi=120)
plt.show()
```

### Envelope (mean ± banda min/max) por janela

```python
fig, ax = plt.subplots(figsize=(9, 4))
for v in videos:
    sub_w = df_windows[df_windows["video_id"] == v].sort_values("window_id").copy()
    sub_w["w_min"] = sub_w["motion_proxy_norm_mean"] - sub_w["motion_proxy_norm_std"].fillna(0)
    sub_w["w_max"] = sub_w["motion_proxy_norm_mean"] + sub_w["motion_proxy_norm_std"].fillna(0)
    ax.plot(sub_w["window_id"], sub_w["motion_proxy_norm_mean"], marker="o", label=f"{v} mean")
    ax.fill_between(sub_w["window_id"], sub_w["w_min"], sub_w["w_max"], alpha=0.2)
ax.set_title("motion_proxy_norm_mean por janela com envelope ±std (REAL)")
ax.set_xlabel("window_id")
ax.set_ylabel("motion_proxy_norm_mean")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "fase5_motion_window_envelope.png", dpi=120)
plt.show()
```

### Histograma de `motion_delta`

```python
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(df_windows["motion_delta"].dropna(), bins=10, edgecolor="black")
ax.set_title("Distribuição de motion_delta por janela (REAL)")
ax.set_xlabel("motion_delta")
ax.set_ylabel("nº de janelas")
fig.tight_layout()
fig.savefig(FIG / "fase5_motion_delta_hist.png", dpi=120)
plt.show()
```

### Estatísticas inferenciais simples por vídeo

```python
def iqr(s):
    q1, q3 = np.percentile(s.dropna(), [25, 75])
    return q3 - q1

stats_real = df_frames.groupby("video_id")["motion_proxy_norm"].agg(
    mean="mean", std="std", iqr=iqr, p95=lambda s: np.percentile(s.dropna(), 95),
    n="count",
).round(4)
stats_real
```

## Heatmap de correlação (REAL, base de janelas)

Filtramos colunas com variância > 0 — isso descarta automaticamente as features zeradas
ou totalmente NaN herdadas do SAMPLE.

```python
num_cols = df_windows.select_dtypes(include=[np.number]).columns.tolist()
var_filter = [c for c in num_cols if df_windows[c].dropna().nunique() > 1]
print(f"Colunas numéricas: {len(num_cols)} | com variância > 0: {len(var_filter)}")
print("Mantidas:", var_filter)

corr_real = df_windows[var_filter].corr(method="spearman")

fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(corr_real, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(var_filter)))
ax.set_xticklabels(var_filter, rotation=45, ha="right")
ax.set_yticks(range(len(var_filter)))
ax.set_yticklabels(var_filter)
for i in range(len(var_filter)):
    for j in range(len(var_filter)):
        ax.text(j, i, f"{corr_real.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
ax.set_title("Correlação Spearman (REAL, janelas, var>0)")
fig.tight_layout()
fig.savefig(FIG / "fase5_corr_heatmap_real.png", dpi=120)
plt.show()
```

> Comentário: como apenas o cluster `motion_proxy_*` tem variância na base atual,
> a matriz se reduz a um pequeno bloco autorrelacionado (motion_proxy_mean,
> motion_proxy_std, motion_proxy_norm_mean, motion_proxy_norm_std, motion_delta) e
> não evidencia relações multivariadas entre dimensões de cena/pose.

## Comparativo REAL vs DEMO

```python
def base_summary(df, name):
    num = df.select_dtypes(include=[np.number])
    return {
        "base": name,
        "n_linhas": len(df),
        "n_colunas": df.shape[1],
        "n_features_com_variancia": int(sum(num[c].dropna().nunique() > 1 for c in num.columns)),
        "n_NaN_total": int(df.isna().sum().sum()),
    }

summary = pd.DataFrame([
    base_summary(df_frames, "REAL frames"),
    base_summary(df_windows, "REAL windows"),
    base_summary(df_demo, "DEMO windows"),
])
summary
```

### Heatmap de correlação (DEMO, todas colunas numéricas)

```python
demo_num_cols = df_demo.select_dtypes(include=[np.number]).columns.tolist()
demo_var_cols = [c for c in demo_num_cols if df_demo[c].dropna().nunique() > 1]
corr_demo = df_demo[demo_var_cols].corr(method="spearman")

fig, ax = plt.subplots(figsize=(10, 9))
im = ax.imshow(corr_demo, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(demo_var_cols)))
ax.set_xticklabels(demo_var_cols, rotation=45, ha="right")
ax.set_yticks(range(len(demo_var_cols)))
ax.set_yticklabels(demo_var_cols)
for i in range(len(demo_var_cols)):
    for j in range(len(demo_var_cols)):
        ax.text(j, i, f"{corr_demo.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6)
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
ax.set_title("Correlação Spearman (DEMO, todas as colunas numéricas)")
fig.tight_layout()
fig.savefig(FIG / "fase5_corr_heatmap_demo.png", dpi=120)
plt.show()
```

> Contraste: a base DEMO exibe relações fortes entre `people_count`, `dense_scene_rate`,
> `risk_score`, `fall_risk_score` e `anomaly_flag` — exatamente o tipo de estrutura
> multivariada que esperamos ver na base REAL **quando** dispusermos de um dataset
> com pessoas detectadas.

## Outliers (regra IQR)

```python
def iqr_outliers(series: pd.Series) -> int:
    s = series.dropna()
    if len(s) < 4 or s.nunique() <= 1:
        return 0
    q1, q3 = np.percentile(s, [25, 75])
    iqr_val = q3 - q1
    lo, hi = q1 - 1.5 * iqr_val, q3 + 1.5 * iqr_val
    return int(((s < lo) | (s > hi)).sum())

real_target_cols = ["motion_proxy", "motion_proxy_norm"]
out_real = pd.DataFrame({
    "feature": real_target_cols,
    "outliers_iqr": [iqr_outliers(df_frames[c]) for c in real_target_cols],
    "n": [df_frames[c].notna().sum() for c in real_target_cols],
})

demo_num = df_demo.select_dtypes(include=[np.number])
out_demo = pd.DataFrame({
    "feature": demo_num.columns,
    "outliers_iqr": [iqr_outliers(demo_num[c]) for c in demo_num.columns],
    "n": [demo_num[c].notna().sum() for c in demo_num.columns],
})

print("=== Outliers REAL ===")
print(out_real)
print("\n=== Outliers DEMO ===")
print(out_demo)
```

## Achados consolidados

1. **F1 — SAMPLE não permite análise multidimensional.** Com `num_people_detected=0`
   em 100% dos frames, todas as features de pose/bbox são NaN ou zero. Apenas a
   dimensão de **movimento agregado** (`motion_proxy` / `motion_proxy_norm` / `motion_delta`)
   é mensurável.
2. **F2 — `motion_proxy` distingue claramente os dois vídeos.** A tabela `stats_real`
   mostra diferença marcante de média e dispersão de `motion_proxy_norm` entre
   `01_001` e `01_002`, confirmando que o sinal de movimento captura variação real
   entre as cenas mesmo sem detecção de pessoas.
3. **F3 — Pipeline analítico está validado.** Todas as transformações
   (carregamento parquet, agrupamento por janela, cálculo de correlação, detecção
   de outliers IQR, geração de figuras) executam ponta-a-ponta sem erro. A
   estrutura está pronta para receber um dataset com mais variância.
4. **F4 — Para a Fase 6 (não supervisionada), recomenda-se adiar até dataset real
   maior OU usar a base DEMO como prova de conceito** com ressalva metodológica
   explícita ("PROVA-DE-CONCEITO — não generaliza").

## Recomendações para Fase 6

- **Caminho A (preferido).** Obter dataset expandido antes de modelar:
  - baixar o ShanghaiTech completo (não apenas o SAMPLE);
  - trocar `pose_landmarker_lite.task` por `pose_landmarker_full.task` para aumentar
    sensibilidade do detector;
  - reprocessar com mais vídeos do split `training` e `testing`.
- **Caminho B (paralelo, baixo custo).** Rodar clustering exploratório
  (KMeans, DBSCAN, IsolationForest) sobre `df_demo` apenas como demonstração
  metodológica, deixando claro no notebook 05 que os resultados não generalizam
  para a base real.

## Próximo passo

Continuar em [`05_unsupervised.md`](05_unsupervised.md) — modelagem não supervisionada
(clusterização e detecção de anomalias). Material complementar consolidado em
[`reports/eda/fase5_eda_inicial.md`](../reports/eda/fase5_eda_inicial.md).
