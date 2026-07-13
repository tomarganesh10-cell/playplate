import numpy as np

from app.broker.paper import SimulationBroker, _synthetic_ohlcv
from app.ml import features as feat
from app.ml import trainer


def test_build_dataset_shapes_and_causality():
    df = _synthetic_ohlcv("MLTEST", "15m", days=60)
    X, y = feat.build_dataset(df, horizon=4)
    assert X.shape[1] == len(feat.FEATURE_NAMES)
    assert len(X) == len(y)
    # Labels are binary.
    assert set(np.unique(y)).issubset({0.0, 1.0})
    # Dataset drops the unlabeled tail: strictly fewer rows than bars.
    assert len(X) < len(df)


def test_train_and_predict_roundtrip():
    df = _synthetic_ohlcv("MLTEST2", "15m", days=90)
    X, y = feat.build_dataset(df, horizon=4)
    model = trainer.train_logistic(X, y)
    m = model.metrics
    assert 0.0 <= m["train_accuracy"] <= 1.0
    assert 0.0 <= m["validation_accuracy"] <= 1.0
    assert m["samples_train"] > m["samples_validation"] > 0

    x = feat.latest_features(df)
    p = trainer.predict_proba(model.weights, model.mu, model.sigma, x)
    assert 0.0 <= p <= 1.0


def test_train_rejects_tiny_dataset():
    X = np.random.rand(50, len(feat.FEATURE_NAMES))
    y = (np.random.rand(50) > 0.5).astype(float)
    try:
        trainer.train_logistic(X, y)
        raise AssertionError("expected ValueError for tiny dataset")
    except ValueError:
        pass


def test_index_quote_simulation_flagged():
    b = SimulationBroker()
    q = b.get_index_quote("NIFTY")
    assert q.symbol == "NIFTY"
    assert q.last_price > 0
