from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


def compute_metrics(y_true: list[int], y_pred: list[int], num_classes: int) -> dict:
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
    per_class_acc = (cm.diagonal() / np.maximum(cm.sum(axis=1), 1)).tolist()
    return {
        "top1_accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "per_class_accuracy": per_class_acc,
        "confusion_matrix": cm,
    }
