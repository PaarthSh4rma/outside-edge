from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models.score import MatchModel, ScoreSnapshotModel
from app.repositories.score_repository import ScoreRepository
from app.schemas.score import (
    CompetitionRead,
    InningsScoreRead,
    MatchRead,
    ScoreSnapshotRead,
    ScoreSyncRead,
    TeamRead,
)
from app.services.score_providers.base import ProviderMatch, ScoreProvider
from app.services.score_providers.registry import get_score_provider


class ScoreService:
    def __init__(
        self,
        provider: ScoreProvider | None = None,
        stale_after_minutes: int | None = None,
    ):
        self.provider = provider or get_score_provider()
        self.stale_after_minutes = (
            stale_after_minutes
            if stale_after_minutes is not None
            else settings.score_stale_after_minutes
        )

    def sync_scores(self, db: Session) -> ScoreSyncRead:
        provider_matches = self._deduplicate_provider_matches(
            self.provider.fetch_live_matches()
            + self.provider.fetch_upcoming_matches()
            + self.provider.fetch_recent_matches()
        )
        result = ScoreRepository(db).sync_matches(
            self.provider.name,
            provider_matches,
            datetime.now(UTC),
        )
        return ScoreSyncRead(**vars(result))

    def get_live_matches(self, db: Session) -> list[MatchRead]:
        return self._to_read_list(ScoreRepository(db).get_live_matches())

    def get_upcoming_matches(self, db: Session) -> list[MatchRead]:
        return self._to_read_list(ScoreRepository(db).get_upcoming_matches())

    def get_recent_matches(self, db: Session) -> list[MatchRead]:
        return self._to_read_list(ScoreRepository(db).get_recent_matches())

    def get_match(self, db: Session, match_id: int) -> MatchRead | None:
        match = ScoreRepository(db).get_match(match_id)
        return self._to_read(match) if match else None

    def _deduplicate_provider_matches(
        self,
        matches: list[ProviderMatch],
    ) -> list[ProviderMatch]:
        return list({match.id: match for match in matches}.values())

    def _to_read_list(self, matches: list[MatchModel]) -> list[MatchRead]:
        return [self._to_read(match) for match in matches]

    def _to_read(self, match: MatchModel) -> MatchRead:
        latest_snapshot = match.snapshots[0] if match.snapshots else None
        return MatchRead(
            id=match.id,
            competition=CompetitionRead(
                id=match.competition.id,
                name=match.competition.name,
                short_name=match.competition.short_name,
                country=match.competition.country,
                season=match.competition.season,
            ),
            home_team=TeamRead(
                id=match.home_team.id,
                name=match.home_team.name,
                short_name=match.home_team.short_name,
            ),
            away_team=TeamRead(
                id=match.away_team.id,
                name=match.away_team.name,
                short_name=match.away_team.short_name,
            ),
            status=match.status,
            format=match.format,
            starts_at=match.starts_at,
            venue=match.venue,
            result_summary=match.result_summary,
            latest_score=self._snapshot_to_read(latest_snapshot),
            is_stale=self._is_stale(match, latest_snapshot),
        )

    def _snapshot_to_read(
        self,
        snapshot: ScoreSnapshotModel | None,
    ) -> ScoreSnapshotRead | None:
        if snapshot is None:
            return None

        return ScoreSnapshotRead(
            id=snapshot.id,
            home_score=[
                InningsScoreRead(**innings) for innings in snapshot.home_score
            ],
            away_score=[
                InningsScoreRead(**innings) for innings in snapshot.away_score
            ],
            status_text=snapshot.status_text,
            detail=snapshot.detail,
            captured_at=snapshot.captured_at,
        )

    def _is_stale(
        self,
        match: MatchModel,
        snapshot: ScoreSnapshotModel | None,
    ) -> bool:
        if match.status != "live" or snapshot is None:
            return False

        captured_at = snapshot.captured_at
        if captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=UTC)

        return captured_at < datetime.now(UTC) - timedelta(
            minutes=self.stale_after_minutes
        )
