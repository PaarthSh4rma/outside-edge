"""Add normalized article URLs for reliable deduplication.

Revision ID: 20260709_0002
Revises: 20260709_0001
Create Date: 2026-07-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from app.services.url_normalizer import normalize_article_url


revision: str = "20260709_0002"
down_revision: str | None = "20260709_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("normalized_url", sa.Text(), nullable=True))

    connection = op.get_bind()
    articles = connection.execute(
        sa.text("SELECT id, url FROM articles ORDER BY id")
    ).mappings()
    seen_urls: set[str] = set()

    for article in articles:
        normalized_url = normalize_article_url(article["url"])
        if normalized_url in seen_urls:
            normalized_url = f"{normalized_url}#legacy-{article['id']}"
        seen_urls.add(normalized_url)
        connection.execute(
            sa.text(
                "UPDATE articles SET normalized_url = :normalized_url WHERE id = :id"
            ),
            {"normalized_url": normalized_url, "id": article["id"]},
        )

    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column(
            "normalized_url",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.create_index(
            "ix_articles_normalized_url",
            ["normalized_url"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_index("ix_articles_normalized_url")
        batch_op.drop_column("normalized_url")
