"""Walk-forward logistic-regression trainer (pure numpy, no extra deps).

Chronological split (train on the first 70%, validate on the last 30%) —
never random shuffling, which would leak future information. Metrics are
reported honestly: validation accuracy ~0.5 means NO edge.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TrainedModel:
    weights: list[float]      # includes bias as last element
    mu: list[float]           # feature means (standardisation)
    sigma: list[float]        # feature stds
    metrics: dict


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def train_logistic(
    X: np.ndarray,
    y: np.ndarray,
    train_frac: float = 0.7,
    epochs: int = 400,
    lr: float = 0.1,
    l2: float = 1e-3,
) -> TrainedModel:
    n = len(X)
    if n < 200:
        raise ValueError(f"Need >=200 samples to train, got {n}")
    split = int(n * train_frac)
    X_tr, y_tr = X[:split], y[:split]
    X_va, y_va = X[split:], y[split:]

    mu = X_tr.mean(axis=0)
    sigma = X_tr.std(axis=0)
    sigma[sigma == 0] = 1.0
    Z_tr = (X_tr - mu) / sigma
    Z_va = (X_va - mu) / sigma

    # Add bias column.
    Z_tr = np.hstack([Z_tr, np.ones((len(Z_tr), 1))])
    Z_va = np.hstack([Z_va, np.ones((len(Z_va), 1))])

    w = np.zeros(Z_tr.shape[1])
    for _ in range(epochs):
        p = _sigmoid(Z_tr @ w)
        grad = Z_tr.T @ (p - y_tr) / len(y_tr) + l2 * w
        w -= lr * grad

    def _acc(Z, yy):
        return float(((_sigmoid(Z @ w) >= 0.5).astype(float) == yy).mean())

    p_va = _sigmoid(Z_va @ w)
    # Brier score: mean squared error of probabilities (lower is better).
    brier = float(((p_va - y_va) ** 2).mean())
    base_rate = float(y_va.mean())

    metrics = {
        "samples_train": int(split),
        "samples_validation": int(n - split),
        "train_accuracy": round(_acc(Z_tr, y_tr), 4),
        "validation_accuracy": round(_acc(Z_va, y_va), 4),
        "validation_base_rate": round(max(base_rate, 1 - base_rate), 4),
        "brier_score": round(brier, 4),
        "note": (
            "Validation accuracy must beat the base rate to indicate any edge. "
            "~0.5 accuracy = no predictive power. Experimental; not advice."
        ),
    }
    return TrainedModel(
        weights=[float(x) for x in w],
        mu=[float(x) for x in mu],
        sigma=[float(x) for x in sigma],
        metrics=metrics,
    )


def predict_proba(model_weights: list[float], mu: list[float], sigma: list[float],
                  features: np.ndarray) -> float:
    z = (features - np.asarray(mu)) / np.asarray(sigma)
    z = np.append(z, 1.0)  # bias
    return float(_sigmoid(z @ np.asarray(model_weights)))
