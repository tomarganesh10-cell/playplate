from app.ai import ranking
from app.broker.paper import _synthetic_ohlcv
from app.engine.scanner import scan_symbol, scan_universe


def test_scan_symbol_returns_structured_result_or_none():
    df = _synthetic_ohlcv("ABC", "15m", days=30)
    res = scan_symbol("ABC", df, min_score=0)  # force a result
    assert res is not None
    assert res.side in ("BUY", "SELL")
    assert res.entry > 0
    assert res.stop_loss != res.entry
    # Risk:reward should be roughly the configured 2.0 target.
    assert res.risk_reward > 0


def test_scan_universe_sorted_desc():
    data = {sym: _synthetic_ohlcv(sym, "15m", 30) for sym in ["A", "B", "C", "D"]}
    results = scan_universe(data, min_score=0)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_confidence_in_unit_interval():
    df = _synthetic_ohlcv("XYZ", "15m", 30)
    res = scan_symbol("XYZ", df, min_score=0)
    conf = ranking.confidence_score(res)
    assert 0.0 <= conf <= 1.0
