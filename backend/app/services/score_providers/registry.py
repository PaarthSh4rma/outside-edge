from app.services.score_providers.base import ScoreProvider
from app.services.score_providers.mock_provider import MockScoreProvider


def get_score_provider() -> ScoreProvider:
    return MockScoreProvider()
