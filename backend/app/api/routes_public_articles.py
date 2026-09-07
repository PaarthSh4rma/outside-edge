from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.article_repository import ArticleRepository
from app.schemas.article import ArticleRead

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleRead])
def get_articles(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
):
    article_repository = ArticleRepository(db)
    latest_articles = article_repository.get_latest(limit=limit)

    return [
        ArticleRead(
            id=article.id,
            title=article.title,
            url=article.url,
            source=article.source,
            published_at=article.published_at,
            summary=article.summary,
            category=article.category,
        )
        for article in latest_articles
    ]
