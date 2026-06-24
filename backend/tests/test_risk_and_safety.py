from cryptography.fernet import Fernet

from app.config import Settings, TradingMode
from app.core.encryption import SecretCipher
from app.risk.circuit_breaker import CircuitBreaker


def test_encryption_roundtrip():
    cipher = SecretCipher(Fernet.generate_key().decode())
    token = cipher.encrypt("super-secret-access-token")
    assert token != "super-secret-access-token"
    assert cipher.decrypt(token) == "super-secret-access-token"


def test_encryption_rejects_unset_key():
    try:
        SecretCipher("CHANGE_ME_fernet_key")
        assert False, "should reject placeholder key"
    except RuntimeError:
        pass


def test_live_trading_gate_requires_both_flags():
    # Mode live but not allowed -> not armed.
    s = Settings(trading_mode=TradingMode.LIVE, allow_live_trading=False, _env_file=None)
    assert s.live_trading_armed is False
    # Allowed but paper mode -> not armed.
    s2 = Settings(trading_mode=TradingMode.PAPER, allow_live_trading=True, _env_file=None)
    assert s2.live_trading_armed is False
    # Both -> armed.
    s3 = Settings(trading_mode=TradingMode.LIVE, allow_live_trading=True, _env_file=None)
    assert s3.live_trading_armed is True


def test_default_mode_is_paper():
    # The *code* default must be the safe paper mode (independent of any env
    # override the test harness sets for isolation).
    assert Settings.model_fields["trading_mode"].default == TradingMode.PAPER
    assert Settings.model_fields["allow_live_trading"].default is False


def test_circuit_breaker_trip_and_reset():
    cb = CircuitBreaker()
    assert cb.tripped is False
    cb.trip("daily loss")
    assert cb.tripped is True
    assert "daily loss" in cb.reason
    cb.reset()
    assert cb.tripped is False
