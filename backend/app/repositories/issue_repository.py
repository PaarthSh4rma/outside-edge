from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.models.article import ArticleModel
from app.models.issue import IssueArticleModel, IssueModel
from app.schemas.article import ArticleRead
from app.schemas.issue import IssueRead, IssueSectionRead


class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_replace_issue(
        self,
        issue_date: date,
        title: str,
        tagline: str,
        sections: list[tuple[str, str, list[ArticleModel]]],
        status: str = "published",
    ) -> IssueModel:
        existing_issue = (
            self.db.query(IssueModel)
            .filter(IssueModel.issue_date == issue_date)
            .first()
        )

        if existing_issue:
            self.db.delete(existing_issue)
            self.db.flush()

        issue = IssueModel(
            issue_date=issue_date,
            title=title,
            tagline=tagline,
            status=status,
        )

        self.db.add(issue)
        self.db.flush()

        for section_name, section_description, articles in sections:
            for rank, article in enumerate(articles, start=1):
                issue_article = IssueArticleModel(
                    issue_id=issue.id,
                    article_id=article.id,
                    section_name=section_name,
                    section_description=section_description,
                    rank=rank,
                )
                self.db.add(issue_article)

        self.db.commit()
        self.db.refresh(issue)

        return issue

    def get_latest_issue(self) -> IssueModel | None:
        return (
            self.db.query(IssueModel)
            .options(joinedload(IssueModel.articles))
            .order_by(IssueModel.issue_date.desc())
            .first()
        )

    def get_published_issues(self, limit: int = 30) -> list[IssueModel]:
        return (
            self.db.query(IssueModel)
            .options(joinedload(IssueModel.articles))
            .filter(IssueModel.status == "published")
            .order_by(IssueModel.issue_date.desc())
            .limit(limit)
            .all()
        )

    def get_published_issue_by_date(self, issue_date: date) -> IssueModel | None:
        return (
            self.db.query(IssueModel)
            .options(joinedload(IssueModel.articles))
            .filter(
                IssueModel.issue_date == issue_date,
                IssueModel.status == "published",
            )
            .first()
        )

    def to_read_schema(self, issue: IssueModel) -> IssueRead:
        grouped_sections: dict[str, dict] = {}

        section_order = {
            "Opening Spell": 1,
            "Powerplay": 2,
            "Around the Grounds": 3,
        }

        sorted_links = sorted(
            issue.articles,
            key=lambda link: (
                section_order.get(link.section_name, 999),
                link.rank,
            ),
        )

        article_ids = [link.article_id for link in sorted_links]

        articles_by_id = {
            article.id: article
            for article in self.db.query(ArticleModel)
            .filter(ArticleModel.id.in_(article_ids))
            .all()
        }

        for link in sorted_links:
            article = articles_by_id.get(link.article_id)

            if not article:
                continue

            if link.section_name not in grouped_sections:
                grouped_sections[link.section_name] = {
                    "name": link.section_name,
                    "description": link.section_description,
                    "articles": [],
                }

            grouped_sections[link.section_name]["articles"].append(
                ArticleRead(
                    id=article.id,
                    title=article.title,
                    url=article.url,
                    source=article.source,
                    published_at=article.published_at,
                    summary=article.summary,
                    category=article.category,
                )
            )

        return IssueRead(
            id=issue.id,
            issue_date=issue.issue_date,
            title=issue.title,
            tagline=issue.tagline,
            status=issue.status,
            sections=[
                IssueSectionRead(**section)
                for section in grouped_sections.values()
            ],
        )
