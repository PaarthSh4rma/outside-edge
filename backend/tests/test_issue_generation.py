from datetime import UTC, date, datetime

from app.repositories.article_repository import ArticleRepository
from app.repositories.issue_repository import IssueRepository
from app.schemas.article import Article
from app.services.issue_service import IssueService


def test_daily_yorker_generation_persists_ranked_sections(db_session):
    article_repository = ArticleRepository(db_session)
    article_repository.create_many_if_not_exists(
        [
            Article(
                title=f"India Test squad update {index}",
                url=f"https://example.com/story-{index}",
                source="Test Feed",
                published_at=datetime(2026, 7, 9, index, tzinfo=UTC),
                summary="World Cup and captain news.",
                category="world_cricket",
            )
            for index in range(10)
        ]
    )

    issue = IssueService().generate_and_save_today_issue(db_session)
    stored_issue = IssueRepository(db_session).get_published_issue_by_date(date.today())

    assert issue.title == "The Daily Yorker"
    assert stored_issue is not None
    assert [section.name for section in issue.sections] == [
        "Opening Spell",
        "Powerplay",
        "Around the Grounds",
    ]
    assert sum(len(section.articles) for section in issue.sections) == 10
