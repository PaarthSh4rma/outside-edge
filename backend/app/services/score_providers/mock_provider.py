from datetime import UTC, datetime, timedelta

from app.services.score_providers.base import (
    ProviderCompetition,
    ProviderInningsScore,
    ProviderMatch,
    ProviderScoreSnapshot,
    ProviderTeam,
    ScoreProvider,
)


class MockScoreProvider(ScoreProvider):
    name = "mock"

    def __init__(self, now: datetime | None = None):
        self.now = now or datetime.now(UTC)

    def fetch_live_matches(self) -> list[ProviderMatch]:
        return [self._matches()["mock-live-test"]]

    def fetch_upcoming_matches(self) -> list[ProviderMatch]:
        matches = self._matches()
        return [matches["mock-upcoming-odi"], matches["mock-upcoming-t20"]]

    def fetch_recent_matches(self) -> list[ProviderMatch]:
        matches = self._matches()
        return [matches["mock-recent-t20"], matches["mock-recent-odi"]]

    def fetch_match(self, provider_match_id: str) -> ProviderMatch | None:
        return self._matches().get(provider_match_id)

    def _matches(self) -> dict[str, ProviderMatch]:
        now = self.now

        australia = ProviderTeam("australia", "Australia", "AUS")
        india = ProviderTeam("india", "India", "IND")
        england = ProviderTeam("england", "England", "ENG")
        new_zealand = ProviderTeam("new-zealand", "New Zealand", "NZ")
        sydney = ProviderTeam("sydney-sixers", "Sydney Sixers", "SIX")
        melbourne = ProviderTeam("melbourne-stars", "Melbourne Stars", "STA")
        south_africa = ProviderTeam("south-africa", "South Africa", "SA")
        pakistan = ProviderTeam("pakistan", "Pakistan", "PAK")
        west_indies = ProviderTeam("west-indies", "West Indies", "WI")
        sri_lanka = ProviderTeam("sri-lanka", "Sri Lanka", "SL")

        return {
            "mock-live-test": ProviderMatch(
                id="mock-live-test",
                competition=ProviderCompetition(
                    "border-gavaskar",
                    "Border-Gavaskar Trophy",
                    "BGT",
                    "Australia",
                    "2026",
                ),
                home_team=australia,
                away_team=india,
                status="live",
                format="Test",
                starts_at=now - timedelta(days=1, hours=4),
                venue="Melbourne Cricket Ground, Melbourne",
                result_summary=None,
                provider_updated_at=now - timedelta(minutes=2),
                score=ProviderScoreSnapshot(
                    home_score=[
                        ProviderInningsScore(1, 287, 10, "91.4"),
                        ProviderInningsScore(2, 42, 1, "14.0"),
                    ],
                    away_score=[ProviderInningsScore(1, 245, 10, "79.3")],
                    status_text="Australia lead by 84 runs",
                    detail="Day 3, Session 1",
                    captured_at=now - timedelta(minutes=2),
                ),
            ),
            "mock-upcoming-odi": ProviderMatch(
                id="mock-upcoming-odi",
                competition=ProviderCompetition(
                    "england-nz-odi",
                    "England v New Zealand ODI Series",
                    "ENG v NZ",
                    "England",
                    "2026",
                ),
                home_team=england,
                away_team=new_zealand,
                status="scheduled",
                format="ODI",
                starts_at=now + timedelta(days=1, hours=2),
                venue="Lord's, London",
                result_summary=None,
                provider_updated_at=now,
                score=ProviderScoreSnapshot(
                    home_score=[],
                    away_score=[],
                    status_text="Match starts tomorrow",
                    detail="10:00 local",
                    captured_at=now,
                ),
            ),
            "mock-upcoming-t20": ProviderMatch(
                id="mock-upcoming-t20",
                competition=ProviderCompetition(
                    "big-bash",
                    "Big Bash League",
                    "BBL",
                    "Australia",
                    "2026/27",
                ),
                home_team=sydney,
                away_team=melbourne,
                status="scheduled",
                format="T20",
                starts_at=now + timedelta(days=3, hours=5),
                venue="Sydney Cricket Ground, Sydney",
                result_summary=None,
                provider_updated_at=now,
                score=ProviderScoreSnapshot(
                    home_score=[],
                    away_score=[],
                    status_text="Match scheduled",
                    detail="19:15 local",
                    captured_at=now,
                ),
            ),
            "mock-recent-t20": ProviderMatch(
                id="mock-recent-t20",
                competition=ProviderCompetition(
                    "sa-pak-t20",
                    "South Africa v Pakistan T20 Series",
                    "SA v PAK",
                    "South Africa",
                    "2026",
                ),
                home_team=south_africa,
                away_team=pakistan,
                status="completed",
                format="T20",
                starts_at=now - timedelta(days=2, hours=4),
                venue="Newlands, Cape Town",
                result_summary="South Africa won by 6 wickets",
                provider_updated_at=now - timedelta(days=2),
                score=ProviderScoreSnapshot(
                    home_score=[ProviderInningsScore(1, 169, 4, "18.3")],
                    away_score=[ProviderInningsScore(1, 165, 8, "20.0")],
                    status_text="South Africa won by 6 wickets",
                    detail="Completed",
                    captured_at=now - timedelta(days=2),
                ),
            ),
            "mock-recent-odi": ProviderMatch(
                id="mock-recent-odi",
                competition=ProviderCompetition(
                    "wi-sl-odi",
                    "West Indies v Sri Lanka ODI Series",
                    "WI v SL",
                    "West Indies",
                    "2026",
                ),
                home_team=west_indies,
                away_team=sri_lanka,
                status="completed",
                format="ODI",
                starts_at=now - timedelta(days=4, hours=5),
                venue="Kensington Oval, Bridgetown",
                result_summary="Sri Lanka won by 18 runs",
                provider_updated_at=now - timedelta(days=4),
                score=ProviderScoreSnapshot(
                    home_score=[ProviderInningsScore(1, 261, 10, "48.2")],
                    away_score=[ProviderInningsScore(1, 279, 7, "50.0")],
                    status_text="Sri Lanka won by 18 runs",
                    detail="Completed",
                    captured_at=now - timedelta(days=4),
                ),
            ),
        }
