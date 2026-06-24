import os

# Ensure tests never touch a real broker/DB and always run in safe mode.
os.environ.setdefault("TRADING_MODE", "simulation")
os.environ.setdefault("ALLOW_LIVE_TRADING", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
# A valid throwaway Fernet key for encryption tests.
os.environ.setdefault("ENCRYPTION_KEY", "RfQhT3n8sd5Yyq3y7sJ2QYH8m1bJ0mQ9rD8wq1mZ5g=")
