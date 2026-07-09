from datetime import UTC, datetime

from app.models.score import (
    CompetitionModel,
    MatchModel,
    ScoreSnapshotModel,
    TeamModel,
)
from app.services.score_providers.mock_provider import MockScoreProvider
from app.services.score_service import ScoreService


def test_mock_score_sync_is_idempotent(db_session):
    provider = MockScoreProvider(now=datetime(2026, 7, 9, 12, 0, tzinfo=UTC))
    service = ScoreService(provider=provider)

    first = service.sync_scores(db_session)
    second = service.sync_scores(db_session)

    assert first.competitions_created == 5
    assert first.teams_created == 10
    assert first.matches_created == 5
    assert first.snapshots_created == 5

    assert second.competitions_created == 0
    assert second.teams_created == 0
    assert second.matches_created == 0
    assert second.matches_updated == 5
    assert second.snapshots_created == 0

    assert db_session.query(CompetitionModel).count() == 5
    assert db_session.query(TeamModel).count() == 10
    assert db_session.query(MatchModel).count() == 5
    assert db_session.query(ScoreSnapshotModel).count() == 5


def test_live_match_staleness_uses_configurable_threshold(db_session):
    provider = MockScoreProvider(now=datetime.now(UTC))
    ScoreService(provider=provider).sync_scores(db_session)

    fresh_match = ScoreService(stale_after_minutes=5).get_live_matches(db_session)[0]
    stale_match = ScoreService(stale_after_minutes=1).get_live_matches(db_session)[0]

    assert fresh_match.is_stale is False
    assert stale_match.is_stale is True
