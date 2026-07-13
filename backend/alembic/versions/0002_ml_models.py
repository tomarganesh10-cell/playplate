"""ml_models table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-13 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ml_models",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("timeframe", sa.String(8), server_default="15m"),
        sa.Column("horizon", sa.Integer, server_default="4"),
        sa.Column("feature_names", sa.JSON),
        sa.Column("weights", sa.JSON),
        sa.Column("mu", sa.JSON),
        sa.Column("sigma", sa.JSON),
        sa.Column("metrics", sa.JSON),
        sa.Column("trained_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ml_models_symbol", "ml_models", ["symbol"])
    op.create_index("ix_ml_models_trained_at", "ml_models", ["trained_at"])


def downgrade() -> None:
    op.drop_table("ml_models")
