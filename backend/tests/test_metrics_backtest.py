from app.backtest import metrics
from app.backtest.engine import BacktestConfig, run_backtest
from app.broker.paper import _synthetic_ohlcv


def test_sharpe_zero_for_constant():
    assert metrics.sharpe_ratio([0.0, 0.0, 0.0]) == 0.0


def test_max_drawdown_simple():
    curve = [100, 120, 90, 110]  # peak 120 -> trough 90 = 25%
    dd = metrics.max_drawdown(curve)
    assert round(dd, 1) == 25.0


def test_summarise_trades_winrate():
    stats = metrics.summarise_trades([100, -50, 200, -25])
    assert stats["total_trades"] == 4
    assert stats["win_rate"] == 0.5
    assert stats["total_pnl"] == 225


def test_summarise_empty():
    stats = metrics.summarise_trades([])
    assert stats["total_trades"] == 0


def test_backtest_runs_and_reports():
    df = _synthetic_ohlcv("TEST", "15m", days=60)
    result = run_backtest("TEST", df, BacktestConfig(warmup=200, min_score=50))
    assert "total_trades" in result.stats
    assert isinstance(result.trades, list)
