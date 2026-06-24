"""Create the first admin user.

Usage (inside the backend container):
    ADMIN_EMAIL=you@example.com ADMIN_PASSWORD='strong-pass' \
        python -m app.scripts.create_admin
If env vars are absent, prompts interactively.
"""
from __future__ import annotations

import getpass
import os
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User


def main() -> int:
    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip()
    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password (>=10 chars): ")
    if len(password) < 10:
        print("Password must be at least 10 characters.", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        if db.execute(select(User).where(User.email == email)).scalar_one_or_none():
            print(f"User {email} already exists.")
            return 0
        user = User(
            email=email,
            full_name="Administrator",
            role="admin",
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Created admin user: {email}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
