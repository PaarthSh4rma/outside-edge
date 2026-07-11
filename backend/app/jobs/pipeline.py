from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.article_repository import ArticleRepository
from app.services.article_service import ArticleService
from app.services.email_service import EmailService
from app.services.issue_service import IssueService


@dataclass(frozen=True)
class FetchNewsResult:
    fetched_count: int
    saved_count: int


@dataclass(frozen=True)
class GenerateIssueResult:
    issue_date: str
    issue_id: int
    article_count: int
    section_counts: dict[str, int]


@dataclass(frozen=True)
class PublishDailyYorkerResult:
    fetched_count: int
    saved_count: int
    issue_date: str
    issue_id: int
    article_count: int
    section_counts: dict[str, int]
    dry_run: bool
    would_send_count: int
    sent_count: int
    skipped_count: int
    failed_count: int


def fetch_news(db: Session) -> FetchNewsResult:
    articles = ArticleService().fetch_latest_articles()
    saved_articles = ArticleRepository(db).create_many_if_not_exists(articles)

    return FetchNewsResult(
        fetched_count=len(articles),
        saved_count=len(saved_articles),
    )


def generate_today_issue(db: Session) -> GenerateIssueResult:
    issue = IssueService().generate_and_save_today_issue(db)
    return _issue_result(issue)


def publish_daily_yorker(
    db: Session,
    *,
    dry_run: bool,
) -> PublishDailyYorkerResult:
    news_result = fetch_news(db)
    issue_result = generate_today_issue(db)
    email_result = EmailService().send_latest(db, dry_run=dry_run)

    return PublishDailyYorkerResult(
        fetched_count=news_result.fetched_count,
        saved_count=news_result.saved_count,
        issue_date=issue_result.issue_date,
        issue_id=issue_result.issue_id,
        article_count=issue_result.article_count,
        section_counts=issue_result.section_counts,
        dry_run=email_result.dry_run,
        would_send_count=email_result.would_send_count,
        sent_count=email_result.sent_count,
        skipped_count=email_result.skipped_count,
        failed_count=email_result.failed_count,
    )


def _issue_result(issue) -> GenerateIssueResult:
    section_counts = {
        section.name: len(section.articles)
        for section in issue.sections
    }

    return GenerateIssueResult(
        issue_date=issue.issue_date.isoformat(),
        issue_id=issue.id,
        article_count=sum(section_counts.values()),
        section_counts=section_counts,
    )
