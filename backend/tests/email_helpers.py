from datetime import UTC, datetime

from app.repositories.article_repository import ArticleRepository
from app.repositories.subscriber_repository import SubscriberRepository
from app.schemas.article import Article
from app.schemas.subscriber import SubscriberCreate
from app.services.email_providers.base import (
    EmailMessage,
    EmailProvider,
    EmailSendResult,
)
from app.services.email_service import EmailService
from app.services.issue_service import IssueService


class FakeEmailProvider(EmailProvider):
    name = "fake"

    def __init__(self, fail_for: set[str] | None = None):
        self.messages: list[EmailMessage] = []
        self.fail_for = fail_for or set()

    def send(self, message: EmailMessage) -> EmailSendResult:
        self.messages.append(message)
        if message.to_email in self.fail_for:
            raise RuntimeError("Provider rejected recipient")
        return EmailSendResult(provider_message_id=f"fake-{len(self.messages)}")


def create_published_issue(db_session):
    ArticleRepository(db_session).create_many_if_not_exists(
        [
            Article(
                title=f"Cricket story {index}",
                url=f"https://example.com/story-{index}",
                source="Test Cricket Desk",
                published_at=datetime(2026, 7, 9, index, tzinfo=UTC),
                summary="A concise cricket update.",
                category="world_cricket",
            )
            for index in range(10)
        ]
    )
    IssueService().generate_and_save_today_issue(db_session)


def create_subscriber(db_session, email: str, *, active: bool = True):
    subscriber = SubscriberRepository(db_session).create_or_reactivate(
        SubscriberCreate(email=email)
    )
    subscriber.is_active = active
    db_session.commit()
    return subscriber


def make_real_send_service(provider):
    return EmailService(
        provider=provider,
        resend_api_key="test-key-never-sent-to-resend",
        safety_dry_run=False,
        email_from="Outside Edge <newsletter@example.com>",
        public_site_url="https://outside-edge.test",
    )
