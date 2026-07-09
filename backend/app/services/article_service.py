from app.schemas.article import Article
from app.services.feed_sources.registry import get_feed_sources
from app.services.url_normalizer import normalize_article_url


class ArticleService:
    def fetch_latest_articles(self) -> list[Article]:
        all_articles: list[Article] = []

        for source in get_feed_sources():
            try:
                articles = source.fetch_articles()
                all_articles.extend(articles)
            except Exception as exc:
                print(f"Failed to fetch articles from {source.__class__.__name__}: {exc}")

        return self._deduplicate_articles(all_articles)

    def _deduplicate_articles(self, articles: list[Article]) -> list[Article]:
        seen_urls: set[str] = set()
        deduplicated: list[Article] = []

        for article in articles:
            article_url = normalize_article_url(str(article.url))

            if article_url in seen_urls:
                continue

            seen_urls.add(article_url)
            deduplicated.append(article)

        return deduplicated
