from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class CompetitionModel(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_competition_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_competition_id",
            name="uq_competition_provider_identity",
        ),
    )


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_team_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_team_id",
            name="uq_team_provider_identity",
        ),
    )


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_match_id: Mapped[str] = mapped_column(String(100), nullable=False)
    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(30), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    venue: Mapped[str | None] = mapped_column(String(250), nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    competition: Mapped[CompetitionModel] = relationship()
    home_team: Mapped[TeamModel] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped[TeamModel] = relationship(foreign_keys=[away_team_id])
    snapshots: Mapped[list["ScoreSnapshotModel"]] = relationship(
        back_populates="match",
        cascade="all, delete-orphan",
        order_by="ScoreSnapshotModel.captured_at.desc()",
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_match_id",
            name="uq_match_provider_identity",
        ),
    )


class ScoreSnapshotModel(Base):
    __tablename__ = "score_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"),
        nullable=False,
        index=True,
    )
    home_score: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    away_score: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    status_text: Mapped[str] = mapped_column(String(250), nullable=False)
    detail: Mapped[str | None] = mapped_column(String(250), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    match: Mapped[MatchModel] = relationship(back_populates="snapshots")

    __table_args__ = (
        UniqueConstraint(
            "match_id",
            "fingerprint",
            name="uq_score_snapshot_fingerprint",
        ),
    )
