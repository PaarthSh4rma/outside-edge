from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProviderCompetition:
    id: str
    name: str
    short_name: str | None = None
    country: str | None = None
    season: str | None = None


@dataclass(frozen=True)
class ProviderTeam:
    id: str
    name: str
    short_name: str


@dataclass(frozen=True)
class ProviderInningsScore:
    innings_number: int
    runs: int
    wickets: int | None
    overs: str
    declared: bool = False


@dataclass(frozen=True)
class ProviderScoreSnapshot:
    home_score: list[ProviderInningsScore]
    away_score: list[ProviderInningsScore]
    status_text: str
    detail: str | None
    captured_at: datetime


@dataclass(frozen=True)
class ProviderMatch:
    id: str
    competition: ProviderCompetition
    home_team: ProviderTeam
    away_team: ProviderTeam
    status: str
    format: str
    starts_at: datetime
    venue: str | None
    result_summary: str | None
    provider_updated_at: datetime
    score: ProviderScoreSnapshot


class ScoreProvider(ABC):
    name: str

    @abstractmethod
    def fetch_live_matches(self) -> list[ProviderMatch]:
        pass

    @abstractmethod
    def fetch_upcoming_matches(self) -> list[ProviderMatch]:
        pass

    @abstractmethod
    def fetch_recent_matches(self) -> list[ProviderMatch]:
        pass

    @abstractmethod
    def fetch_match(self, provider_match_id: str) -> ProviderMatch | None:
        pass
