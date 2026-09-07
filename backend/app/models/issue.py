from datetime import UTC, date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class IssueModel(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    tagline: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    articles: Mapped[list["IssueArticleModel"]] = relationship(
        back_populates="issue",
        cascade="all, delete-orphan",
    )


class IssueArticleModel(Base):
    __tablename__ = "issue_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)

    section_name: Mapped[str] = mapped_column(String(100), nullable=False)
    section_description: Mapped[str] = mapped_column(Text, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    issue: Mapped["IssueModel"] = relationship(back_populates="articles")

    __table_args__ = (
        UniqueConstraint("issue_id", "article_id", name="uq_issue_article"),
    )
