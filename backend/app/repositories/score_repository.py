import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.score import (
    CompetitionModel,
    MatchModel,
    ScoreSnapshotModel,
    TeamModel,
)
from app.services.score_providers.base import ProviderMatch, ProviderTeam


@dataclass
class ScoreSyncResult:
    competitions_created: int = 0
    teams_created: int = 0
    matches_created: int = 0
    matches_updated: int = 0
    snapshots_created: int = 0


class ScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def sync_matches(
        self,
        provider: str,
        matches: list[ProviderMatch],
        synced_at: datetime,
    ) -> ScoreSyncResult:
        result = ScoreSyncResult()
        competition_cache: dict[str, CompetitionModel] = {}
        team_cache: dict[str, TeamModel] = {}

        try:
            for provider_match in matches:
                competition = self._upsert_competition(
                    provider,
                    provider_match,
                    competition_cache,
                    result,
                )
                home_team = self._upsert_team(
                    provider,
                    provider_match.home_team,
                    team_cache,
                    result,
                )
                away_team = self._upsert_team(
                    provider,
                    provider_match.away_team,
                    team_cache,
                    result,
                )
                match = self._upsert_match(
                    provider,
                    provider_match,
                    competition,
                    home_team,
                    away_team,
                    synced_at,
                    result,
                )
                self._upsert_snapshot(match, provider_match, result)

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return result

    def get_live_matches(self) -> list[MatchModel]:
        return self._base_match_query().filter(MatchModel.status == "live").order_by(
            MatchModel.starts_at.asc()
        ).all()

    def get_upcoming_matches(self) -> list[MatchModel]:
        return self._base_match_query().filter(
            MatchModel.status == "scheduled"
        ).order_by(MatchModel.starts_at.asc()).all()

    def get_recent_matches(self, limit: int = 20) -> list[MatchModel]:
        return self._base_match_query().filter(
            MatchModel.status == "completed"
        ).order_by(MatchModel.starts_at.desc()).limit(limit).all()

    def get_match(self, match_id: int) -> MatchModel | None:
        return self._base_match_query().filter(MatchModel.id == match_id).first()

    def _base_match_query(self):
        return self.db.query(MatchModel).options(
            joinedload(MatchModel.competition),
            joinedload(MatchModel.home_team),
            joinedload(MatchModel.away_team),
            joinedload(MatchModel.snapshots),
        )

    def _upsert_competition(
        self,
        provider: str,
        provider_match: ProviderMatch,
        cache: dict[str, CompetitionModel],
        result: ScoreSyncResult,
    ) -> CompetitionModel:
        source = provider_match.competition
        if source.id in cache:
            return cache[source.id]

        competition = (
            self.db.query(CompetitionModel)
            .filter(
                CompetitionModel.provider == provider,
                CompetitionModel.provider_competition_id == source.id,
            )
            .first()
        )

        if competition is None:
            competition = CompetitionModel(
                provider=provider,
                provider_competition_id=source.id,
                name=source.name,
                short_name=source.short_name,
                country=source.country,
                season=source.season,
            )
            self.db.add(competition)
            self.db.flush()
            result.competitions_created += 1
        else:
            competition.name = source.name
            competition.short_name = source.short_name
            competition.country = source.country
            competition.season = source.season

        cache[source.id] = competition
        return competition

    def _upsert_team(
        self,
        provider: str,
        source: ProviderTeam,
        cache: dict[str, TeamModel],
        result: ScoreSyncResult,
    ) -> TeamModel:
        if source.id in cache:
            return cache[source.id]

        team = (
            self.db.query(TeamModel)
            .filter(
                TeamModel.provider == provider,
                TeamModel.provider_team_id == source.id,
            )
            .first()
        )

        if team is None:
            team = TeamModel(
                provider=provider,
                provider_team_id=source.id,
                name=source.name,
                short_name=source.short_name,
            )
            self.db.add(team)
            self.db.flush()
            result.teams_created += 1
        else:
            team.name = source.name
            team.short_name = source.short_name

        cache[source.id] = team
        return team

    def _upsert_match(
        self,
        provider: str,
        source: ProviderMatch,
        competition: CompetitionModel,
        home_team: TeamModel,
        away_team: TeamModel,
        synced_at: datetime,
        result: ScoreSyncResult,
    ) -> MatchModel:
        match = (
            self.db.query(MatchModel)
            .filter(
                MatchModel.provider == provider,
                MatchModel.provider_match_id == source.id,
            )
            .first()
        )

        if match is None:
            match = MatchModel(
                provider=provider,
                provider_match_id=source.id,
                competition_id=competition.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                status=source.status,
                format=source.format,
                starts_at=source.starts_at,
                venue=source.venue,
                result_summary=source.result_summary,
                provider_updated_at=source.provider_updated_at,
                last_synced_at=synced_at,
            )
            self.db.add(match)
            self.db.flush()
            result.matches_created += 1
        else:
            match.competition_id = competition.id
            match.home_team_id = home_team.id
            match.away_team_id = away_team.id
            match.status = source.status
            match.format = source.format
            match.starts_at = source.starts_at
            match.venue = source.venue
            match.result_summary = source.result_summary
            match.provider_updated_at = source.provider_updated_at
            match.last_synced_at = synced_at
            result.matches_updated += 1

        return match

    def _upsert_snapshot(
        self,
        match: MatchModel,
        source: ProviderMatch,
        result: ScoreSyncResult,
    ) -> None:
        home_score = [asdict(innings) for innings in source.score.home_score]
        away_score = [asdict(innings) for innings in source.score.away_score]
        fingerprint = self._snapshot_fingerprint(
            home_score,
            away_score,
            source.score.status_text,
            source.score.detail,
        )
        snapshot = (
            self.db.query(ScoreSnapshotModel)
            .filter(
                ScoreSnapshotModel.match_id == match.id,
                ScoreSnapshotModel.fingerprint == fingerprint,
            )
            .first()
        )

        if snapshot is not None:
            snapshot.captured_at = source.score.captured_at
            return

        self.db.add(
            ScoreSnapshotModel(
                match_id=match.id,
                home_score=home_score,
                away_score=away_score,
                status_text=source.score.status_text,
                detail=source.score.detail,
                captured_at=source.score.captured_at,
                fingerprint=fingerprint,
            )
        )
        result.snapshots_created += 1

    def _snapshot_fingerprint(
        self,
        home_score: list[dict],
        away_score: list[dict],
        status_text: str,
        detail: str | None,
    ) -> str:
        payload = json.dumps(
            {
                "home_score": home_score,
                "away_score": away_score,
                "status_text": status_text,
                "detail": detail,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
