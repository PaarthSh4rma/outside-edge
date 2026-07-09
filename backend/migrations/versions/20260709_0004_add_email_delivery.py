"""Add newsletter delivery and unsubscribe tables.

Revision ID: 20260709_0004
Revises: 20260709_0003
Create Date: 2026-07-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260709_0004"
down_revision: str | None = "20260709_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("subscriber_id", sa.Integer(), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_message_id", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.ForeignKeyConstraint(["subscriber_id"], ["subscribers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "issue_id",
            "subscriber_id",
            "attempt_number",
            name="uq_email_delivery_attempt",
        ),
    )
    op.create_index(
        op.f("ix_email_deliveries_id"),
        "email_deliveries",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_deliveries_issue_id"),
        "email_deliveries",
        ["issue_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_deliveries_status"),
        "email_deliveries",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_deliveries_subscriber_id"),
        "email_deliveries",
        ["subscriber_id"],
        unique=False,
    )

    op.create_table(
        "unsubscribe_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subscriber_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["subscriber_id"], ["subscribers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        op.f("ix_unsubscribe_tokens_id"),
        "unsubscribe_tokens",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unsubscribe_tokens_subscriber_id"),
        "unsubscribe_tokens",
        ["subscriber_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_unsubscribe_tokens_subscriber_id"),
        table_name="unsubscribe_tokens",
    )
    op.drop_index(op.f("ix_unsubscribe_tokens_id"), table_name="unsubscribe_tokens")
    op.drop_table("unsubscribe_tokens")
    op.drop_index(
        op.f("ix_email_deliveries_subscriber_id"),
        table_name="email_deliveries",
    )
    op.drop_index(op.f("ix_email_deliveries_status"), table_name="email_deliveries")
    op.drop_index(op.f("ix_email_deliveries_issue_id"), table_name="email_deliveries")
    op.drop_index(op.f("ix_email_deliveries_id"), table_name="email_deliveries")
    op.drop_table("email_deliveries")
