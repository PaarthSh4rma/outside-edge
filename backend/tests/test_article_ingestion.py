from datetime import UTC, datetime

from app.repositories.article_repository import ArticleRepository
from app.schemas.article import Article
from app.services.article_service import ArticleService


def make_article(url: str, title: str = "Australia wins the Test") -> Article:
    return Article(
        title=title,
        url=url,
        source="Test Feed",
        published_at=datetime(2026, 7, 9, tzinfo=UTC),
        summary="A match report.",
        category="world_cricket",
    )


def test_feed_ingestion_deduplicates_normalized_urls(monkeypatch):
    class Feed:
        def fetch_articles(self):
            return [
                make_article("https://example.com/story?utm_source=rss"),
                make_article("https://EXAMPLE.com/story/#score", "Duplicate title"),
            ]

    monkeypatch.setattr(
        "app.services.article_service.get_feed_sources",
        lambda: [Feed()],
    )

    articles = ArticleService().fetch_latest_articles()

    assert len(articles) == 1
    assert articles[0].title == "Australia wins the Test"


def test_repository_bulk_insert_is_transactional_and_idempotent(db_session):
    repository = ArticleRepository(db_session)
    articles = [
        make_article("https://example.com/story?utm_medium=email"),
        make_article("https://example.com/story/", "Duplicate title"),
    ]

    first_result = repository.create_many_if_not_exists(articles)
    second_result = repository.create_many_if_not_exists(articles)

    assert len(first_result) == 1
    assert len(second_result) == 1
    assert first_result[0].id == second_result[0].id
    assert repository.get_latest() == first_result
