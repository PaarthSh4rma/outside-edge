from datetime import UTC, datetime

from app.jobs.pipeline import fetch_news, generate_today_issue, publish_daily_yorker
from app.models.email import EmailDeliveryModel
from app.repositories.article_repository import ArticleRepository
from app.repositories.issue_repository import IssueRepository
from app.schemas.article import Article
from tests.email_helpers import create_subscriber


def make_article(index: int, url: str | None = None) -> Article:
    return Article(
        title=f"Cricket job story {index}",
        url=url or f"https://example.com/job-story-{index}",
        source="Job Test Feed",
        published_at=datetime(2026, 7, 9, index, tzinfo=UTC),
        summary="A concise cricket update.",
        category="world_cricket",
    )


def test_fetch_news_job_persists_deduped_articles(db_session, monkeypatch):
    class Feed:
        def fetch_articles(self):
            return [
                make_article(1, "https://example.com/story?utm_source=rss"),
                make_article(2, "https://example.com/story/"),
                make_article(3, "https://example.com/other-story"),
            ]

    monkeypatch.setattr(
        "app.services.article_service.get_feed_sources",
        lambda: [Feed()],
    )

    first_result = fetch_news(db_session)
    second_result = fetch_news(db_session)

    assert first_result.fetched_count == 2
    assert first_result.saved_count == 2
    assert second_result.fetched_count == 2
    assert second_result.saved_count == 2
    assert len(ArticleRepository(db_session).get_latest()) == 2


def test_generate_issue_job_reports_section_counts(db_session):
    ArticleRepository(db_session).create_many_if_not_exists(
        [make_article(index) for index in range(10)]
    )

    result = generate_today_issue(db_session)

    assert result.issue_id > 0
    assert result.article_count == 10
    assert result.section_counts == {
        "Opening Spell": 3,
        "Powerplay": 5,
        "Around the Grounds": 2,
    }


def test_publish_daily_yorker_dry_run_is_safe_to_rerun(db_session, monkeypatch):
    class Feed:
        def fetch_articles(self):
            return [make_article(index) for index in range(10)]

    monkeypatch.setattr(
        "app.services.article_service.get_feed_sources",
        lambda: [Feed()],
    )
    create_subscriber(db_session, "reader@example.com")

    first_result = publish_daily_yorker(db_session, dry_run=True)
    second_result = publish_daily_yorker(db_session, dry_run=True)
    issue = IssueRepository(db_session).get_latest_issue()

    assert issue is not None
    assert first_result.issue_id == issue.id
    assert second_result.issue_id == issue.id
    assert first_result.would_send_count == 1
    assert second_result.would_send_count == 1
    assert first_result.sent_count == 0
    assert second_result.sent_count == 0
    assert db_session.query(EmailDeliveryModel).count() == 0


def test_publish_daily_yorker_send_respects_email_dry_run_safety(db_session, monkeypatch):
    class Feed:
        def fetch_articles(self):
            return [make_article(index) for index in range(10)]

    monkeypatch.setattr(
        "app.services.article_service.get_feed_sources",
        lambda: [Feed()],
    )
    create_subscriber(db_session, "reader@example.com")

    result = publish_daily_yorker(db_session, dry_run=False)

    assert result.dry_run is True
    assert result.would_send_count == 1
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert db_session.query(EmailDeliveryModel).count() == 0
