from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.article_repository import ArticleRepository
from app.services.article_service import ArticleService
from app.security import require_admin_api_key

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)


@router.post("/fetch-news")
def fetch_news(db: Session = Depends(get_db)):
    article_service = ArticleService()
    article_repository = ArticleRepository(db)

    articles = article_service.fetch_latest_articles()
    saved_articles = article_repository.create_many_if_not_exists(articles)

    return {
        "fetched_count": len(articles),
        "saved_count": len(saved_articles),
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "published_at": article.published_at,
                "summary": article.summary,
                "category": article.category,
            }
            for article in saved_articles
        ],
    }
