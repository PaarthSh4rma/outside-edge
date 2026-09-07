from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.issue import IssueArticleModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class ArticleModel(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    normalized_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    issue_links: Mapped[list["IssueArticleModel"]] = relationship()
