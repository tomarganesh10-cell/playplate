"""Symmetric encryption for secrets at rest (broker tokens, API secrets).

Uses Fernet (AES-128-CBC + HMAC). The key comes from ENCRYPTION_KEY.
"""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class SecretCipher:
    def __init__(self, key: str) -> None:
        if not key or key.startswith("CHANGE_ME"):
            # Fail loudly rather than silently storing plaintext-equivalent secrets.
            raise RuntimeError(
                "ENCRYPTION_KEY is not configured. Generate one with: "
                "python -c \"from cryptography.fernet import Fernet;"
                "print(Fernet.generate_key().decode())\""
            )
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except InvalidToken as exc:  # pragma: no cover - corruption path
            raise ValueError("Failed to decrypt secret (key rotated or data corrupt)") from exc


_cipher: SecretCipher | None = None


def get_cipher() -> SecretCipher:
    global _cipher
    if _cipher is None:
        _cipher = SecretCipher(settings.encryption_key)
    return _cipher
