from app.broker import instruments


class _FakeKite:
    def __init__(self, rows):
        self._rows = rows
        self.calls = 0

    def instruments(self, exchange):
        self.calls += 1
        assert exchange == "NSE"
        return self._rows


_ROWS = [
    {"tradingsymbol": "RELIANCE", "instrument_token": 738561, "segment": "NSE", "instrument_type": "EQ"},
    {"tradingsymbol": "TCS", "instrument_token": 2953217, "segment": "NSE", "instrument_type": "EQ"},
    {"tradingsymbol": "NIFTY 50", "instrument_token": 256265, "segment": "INDICES", "instrument_type": "EQ"},
]


def setup_function():
    # Reset module cache between tests.
    instruments._cache = {}
    instruments._cache_day = None


def test_loads_only_nse_equities():
    kite = _FakeKite(_ROWS)
    mapping = instruments.load_nse_equity_tokens(kite)
    assert mapping == {"RELIANCE": 738561, "TCS": 2953217}
    assert "NIFTY 50" not in mapping  # index filtered out


def test_caches_within_day():
    kite = _FakeKite(_ROWS)
    instruments.load_nse_equity_tokens(kite)
    instruments.load_nse_equity_tokens(kite)
    assert kite.calls == 1  # second call served from cache


def test_force_refresh_rehits():
    kite = _FakeKite(_ROWS)
    instruments.load_nse_equity_tokens(kite)
    instruments.load_nse_equity_tokens(kite, force=True)
    assert kite.calls == 2
