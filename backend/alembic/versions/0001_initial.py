"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), server_default="trader"),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("timeframe", sa.String(8), server_default="15m"),
        sa.Column("entry", sa.Float, nullable=False),
        sa.Column("stop_loss", sa.Float, nullable=False),
        sa.Column("target", sa.Float, nullable=False),
        sa.Column("risk_reward", sa.Float, server_default="0"),
        sa.Column("score", sa.Float, server_default="0"),
        sa.Column("confidence", sa.Float, server_default="0"),
        sa.Column("rank", sa.Integer),
        sa.Column("indicators", sa.JSON),
        sa.Column("explanation", sa.String(4000)),
        sa.Column("status", sa.String(16), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_signals_symbol", "signals", ["symbol"])
    op.create_index("ix_signals_created_at", "signals", ["created_at"])

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("signal_id", sa.Integer, sa.ForeignKey("signals.id")),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("mode", sa.String(16), server_default="paper"),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("entry_price", sa.Float, nullable=False),
        sa.Column("exit_price", sa.Float),
        sa.Column("stop_loss", sa.Float),
        sa.Column("target", sa.Float),
        sa.Column("pnl", sa.Float, server_default="0"),
        sa.Column("fees", sa.Float, server_default="0"),
        sa.Column("status", sa.String(16), server_default="open"),
        sa.Column("broker_order_id", sa.String(64)),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_trades_symbol", "trades", ["symbol"])
    op.create_index("ix_trades_signal_id", "trades", ["signal_id"])
    op.create_index("ix_trades_opened_at", "trades", ["opened_at"])

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False, unique=True),
        sa.Column("quantity", sa.Integer, server_default="0"),
        sa.Column("avg_price", sa.Float, server_default="0"),
        sa.Column("last_price", sa.Float, server_default="0"),
        sa.Column("unrealised_pnl", sa.Float, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_positions_symbol", "positions", ["symbol"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor_id", sa.Integer),
        sa.Column("actor_email", sa.String(255)),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target", sa.String(255)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("detail", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    op.create_table(
        "broker_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("broker", sa.String(32), server_default="zerodha"),
        sa.Column("api_key", sa.String(255)),
        sa.Column("encrypted_access_token", sa.Text),
        sa.Column("user_id", sa.String(64)),
        sa.Column("is_valid", sa.Boolean, server_default=sa.true()),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_broker_sessions_broker", "broker_sessions", ["broker"])


def downgrade() -> None:
    op.drop_table("broker_sessions")
    op.drop_table("audit_logs")
    op.drop_table("positions")
    op.drop_table("trades")
    op.drop_table("signals")
    op.drop_table("users")
