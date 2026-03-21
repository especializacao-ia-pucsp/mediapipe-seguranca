from __future__ import annotations

from typing import Any


def summarize_classification(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = sorted(set(y_true) | set(y_pred))
    label_to_index = {label: index for index, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]

    correct_predictions = 0
    for expected, predicted in zip(y_true, y_pred, strict=True):
        matrix[label_to_index[expected]][label_to_index[predicted]] += 1
        if expected == predicted:
            correct_predictions += 1

    accuracy = correct_predictions / len(y_true) if y_true else 0.0
    return {
        "accuracy": float(accuracy),
        "labels": labels,
        "confusion_matrix": matrix,
    }
