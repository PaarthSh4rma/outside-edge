from datetime import datetime

from pydantic import BaseModel


class CompetitionRead(BaseModel):
    id: int
    name: str
    short_name: str | None
    country: str | None
    season: str | None


class TeamRead(BaseModel):
    id: int
    name: str
    short_name: str


class InningsScoreRead(BaseModel):
    innings_number: int
    runs: int
    wickets: int | None
    overs: str
    declared: bool = False


class ScoreSnapshotRead(BaseModel):
    id: int
    home_score: list[InningsScoreRead]
    away_score: list[InningsScoreRead]
    status_text: str
    detail: str | None
    captured_at: datetime


class MatchRead(BaseModel):
    id: int
    competition: CompetitionRead
    home_team: TeamRead
    away_team: TeamRead
    status: str
    format: str
    starts_at: datetime
    venue: str | None
    result_summary: str | None
    latest_score: ScoreSnapshotRead | None
    is_stale: bool


class ScoreSyncRead(BaseModel):
    competitions_created: int
    teams_created: int
    matches_created: int
    matches_updated: int
    snapshots_created: int
