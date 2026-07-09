from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.article import ArticleModel
from app.schemas.article import Article
from app.services.url_normalizer import normalize_article_url


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_if_not_exists(self, article: Article) -> ArticleModel:
        return self.create_many_if_not_exists([article])[0]

    def create_many_if_not_exists(self, articles: list[Article]) -> list[ArticleModel]:
        if not articles:
            return []

        values_by_url: dict[str, dict] = {}
        ordered_urls: list[str] = []

        for article in articles:
            normalized_url = normalize_article_url(str(article.url))
            if normalized_url in values_by_url:
                continue

            ordered_urls.append(normalized_url)
            values_by_url[normalized_url] = {
                "title": article.title,
                "url": str(article.url),
                "normalized_url": normalized_url,
                "source": article.source,
                "published_at": article.published_at,
                "summary": article.summary,
                "category": article.category,
            }

        statement = self._insert_statement(list(values_by_url.values()))
        self.db.execute(statement)
        self.db.commit()

        saved_by_url = {
            article.normalized_url: article
            for article in self.db.query(ArticleModel)
            .filter(ArticleModel.normalized_url.in_(ordered_urls))
            .all()
        }

        return [saved_by_url[url] for url in ordered_urls]

    def _insert_statement(self, values: list[dict]):
        dialect_name = self.db.get_bind().dialect.name

        if dialect_name == "postgresql":
            return postgres_insert(ArticleModel).values(values).on_conflict_do_nothing(
                index_elements=[ArticleModel.normalized_url]
            )
        if dialect_name == "sqlite":
            return sqlite_insert(ArticleModel).values(values).on_conflict_do_nothing(
                index_elements=[ArticleModel.normalized_url]
            )

        return insert(ArticleModel).values(values)

    def get_latest(self, limit: int = 50) -> list[ArticleModel]:
        return (
            self.db.query(ArticleModel)
            .order_by(ArticleModel.published_at.desc().nullslast(), ArticleModel.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_latest_models(self, limit: int = 50) -> list[ArticleModel]:
        return (
            self.db.query(ArticleModel)
            .order_by(ArticleModel.published_at.desc().nullslast(), ArticleModel.created_at.desc())
            .limit(limit)
            .all()
        )
