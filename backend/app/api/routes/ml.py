"""Experimental ML endpoints: train on broker historical data, then predict.

Every response carries an explicit experimental/no-advice disclaimer, and
training metrics are reported honestly (validation accuracy vs base rate).
"""
from __future__ import annotations

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase
from app.database import get_db
from app.deps import get_broker_dep, get_current_user
from app.ml import features as feat
from app.ml import trainer
from app.models.ml_model import MLModel
from app.models.user import User
from app.services import audit

router = APIRouter()

_DISCLAIMER = (
    "Experimental research model. Probabilities are NOT predictions of the "
    "future and NOT investment advice. Validation accuracy near the base "
    "rate means the model has no edge. Trading involves risk of loss."
)

# Index pseudo-symbols route to index historical data on supported brokers;
# in simulation they use synthetic series.
TRAINABLE_INDICES = {"NIFTY", "SENSEX", "BANKNIFTY", "FINNIFTY"}


@router.post("/train")
def train(
    symbol: str = Query(..., description="NSE symbol or index (NIFTY/SENSEX)"),
    timeframe: str = Query("15m"),
    days: int = Query(120, ge=30, le=730),
    horizon: int = Query(4, ge=1, le=50, description="Forward bars for the label"),
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    user: User = Depends(get_current_user),
) -> dict:
    sym = symbol.upper()
    df = broker.historical_ohlcv(sym, timeframe, days=days)
    if len(df) < 250:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough history for {sym} ({len(df)} bars); need >=250.",
        )

    X, y = feat.build_dataset(df, horizon=horizon)
    try:
        model = trainer.train_logistic(X, y)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    row = MLModel(
        symbol=sym, timeframe=timeframe, horizon=horizon,
        feature_names=feat.FEATURE_NAMES, weights=model.weights,
        mu=model.mu, sigma=model.sigma, metrics=model.metrics,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    audit.record(
        db, "ml_model_trained", actor_id=user.id, actor_email=user.email,
        target=sym, detail={"model_id": row.id, "metrics": model.metrics},
    )
    return {
        "model_id": row.id,
        "symbol": sym,
        "timeframe": timeframe,
        "horizon_bars": horizon,
        "metrics": model.metrics,
        "disclaimer": _DISCLAIMER,
    }


@router.get("/predict/{symbol}")
def predict(
    symbol: str,
    timeframe: str = Query("15m"),
    db: Session = Depends(get_db),
    broker: BrokerBase = Depends(get_broker_dep),
    _: User = Depends(get_current_user),
) -> dict:
    sym = symbol.upper()
    row = db.execute(
        select(MLModel).where(MLModel.symbol == sym).order_by(MLModel.trained_at.desc())
    ).scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No trained model for {sym}. POST /api/ml/train first.")

    df = broker.historical_ohlcv(sym, timeframe, days=30)
    if len(df) < 210:
        raise HTTPException(status_code=422, detail="Not enough recent data to build features.")
    x = feat.latest_features(df)
    if not np.isfinite(x).all():
        raise HTTPException(status_code=422, detail="Feature computation produced NaNs.")

    prob_up = trainer.predict_proba(row.weights, row.mu, row.sigma, x)
    return {
        "symbol": sym,
        "model_id": row.id,
        "trained_at": row.trained_at.isoformat(),
        "horizon_bars": row.horizon,
        "prob_up": round(prob_up, 4),
        "prob_down": round(1 - prob_up, 4),
        "validation_accuracy": row.metrics.get("validation_accuracy"),
        "validation_base_rate": row.metrics.get("validation_base_rate"),
        "disclaimer": _DISCLAIMER,
    }


@router.get("/models")
def list_models(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> list[dict]:
    rows = db.execute(select(MLModel).order_by(MLModel.trained_at.desc()).limit(50)).scalars()
    return [
        {
            "id": r.id, "symbol": r.symbol, "timeframe": r.timeframe,
            "horizon": r.horizon, "metrics": r.metrics,
            "trained_at": r.trained_at.isoformat(),
        }
        for r in rows
    ]
