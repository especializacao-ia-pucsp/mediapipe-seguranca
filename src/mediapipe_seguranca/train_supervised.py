from __future__ import annotations

import numpy as np
import pandas as pd

from .evaluate import summarize_classification
from .train_unsupervised import FEATURE_COLUMNS


def run_supervised_baseline(features: pd.DataFrame) -> dict[str, object]:
    if features["label"].nunique() < 2:
        raise ValueError("São necessárias pelo menos duas classes para treino supervisionado.")

    train_parts = []
    test_parts = []
    for _, group in features.groupby("label"):
        split_index = max(1, int(np.ceil(len(group) * 0.6)))
        train_parts.append(group.iloc[:split_index])
        test_parts.append(group.iloc[split_index:])

    train_df = pd.concat(train_parts, ignore_index=True)
    test_df = pd.concat(test_parts, ignore_index=True)
    if test_df.empty:
        test_df = train_df.copy()

    centroids = (
        train_df.groupby("label")[FEATURE_COLUMNS]
        .mean()
        .to_dict(orient="index")
    )

    predictions: list[str] = []
    for row in test_df[FEATURE_COLUMNS].itertuples(index=False, name=None):
        values = np.array(row, dtype=float)
        best_label = min(
            centroids,
            key=lambda label: float(np.linalg.norm(values - np.array(list(centroids[label].values()), dtype=float))),
        )
        predictions.append(best_label)

    metrics = summarize_classification(test_df["label"].tolist(), predictions)
    return {
        "model": "centroid-baseline",
        "metrics": metrics,
        "test_rows": len(test_df),
    }
