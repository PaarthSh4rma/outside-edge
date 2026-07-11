from datetime import date

from sqlalchemy.orm import Session

from app.models.article import ArticleModel
from app.repositories.article_repository import ArticleRepository
from app.repositories.issue_repository import IssueRepository
from app.schemas.article import Article
from app.schemas.issue import Issue, IssueSection
from app.services.article_service import ArticleService
from app.services.ranking_service import ArticleRankingService


class IssueService:
    """
    Builds a Daily Yorker issue.

    It supports:
    - in-memory generation for fast development
    - database-backed generation for the public product
    """

    def __init__(
        self,
        article_service: ArticleService | None = None,
        ranking_service: ArticleRankingService | None = None,
    ):
        self.article_service = article_service or ArticleService()
        self.ranking_service = ranking_service or ArticleRankingService()

    def generate_today_issue(self) -> Issue:
        articles = self.article_service.fetch_latest_articles()
        ranked_articles = self.ranking_service.rank_articles(articles)

        return Issue(
            issue_date=date.today(),
            title="The Daily Yorker",
            tagline="Cricket news, caught daily.",
            sections=self._build_sections(ranked_articles),
        )

    def generate_and_save_today_issue(self, db: Session):
        article_repository = ArticleRepository(db)
        issue_repository = IssueRepository(db)

        latest_article_models = article_repository.get_latest_models(limit=50)

        ranked_article_models = self._rank_article_models(latest_article_models)

        sections = self._build_model_sections(ranked_article_models)

        issue = issue_repository.create_or_replace_issue(
            issue_date=date.today(),
            title="The Daily Yorker",
            tagline="Cricket news, caught daily.",
            sections=sections,
            status="published",
        )

        return issue_repository.to_read_schema(issue)

    def _build_sections(self, articles: list[Article]) -> list[IssueSection]:
        opening_spell = articles[:3]
        powerplay = articles[3:8]
        around_the_grounds = articles[8:15]

        return [
            IssueSection(
                name="Opening Spell",
                description="The biggest cricket stories of the day.",
                articles=opening_spell,
            ),
            IssueSection(
                name="Powerplay",
                description="Quick updates worth knowing.",
                articles=powerplay,
            ),
            IssueSection(
                name="Around the Grounds",
                description="More stories from across world cricket.",
                articles=around_the_grounds,
            ),
        ]

    def _build_model_sections(
        self,
        articles: list[ArticleModel],
    ) -> list[tuple[str, str, list[ArticleModel]]]:
        return [
            (
                "Opening Spell",
                "The biggest cricket stories of the day.",
                articles[:3],
            ),
            (
                "Powerplay",
                "Quick updates worth knowing.",
                articles[3:8],
            ),
            (
                "Around the Grounds",
                "More stories from across world cricket.",
                articles[8:15],
            ),
        ]

    def _rank_article_models(self, articles: list[ArticleModel]) -> list[ArticleModel]:
        return sorted(
            articles,
            key=self._score_article_model,
            reverse=True,
        )

    def _score_article_model(self, article: ArticleModel) -> int:
        article_schema = Article(
            title=article.title,
            url=article.url,
            source=article.source,
            published_at=article.published_at,
            summary=article.summary,
            category=article.category,
        )

        return self.ranking_service.score_article(article_schema)
