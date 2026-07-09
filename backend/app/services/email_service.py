from datetime import date

from sqlalchemy.orm import Session

from app.config import settings
from app.models.issue import IssueModel
from app.models.subscriber import SubscriberModel
from app.repositories.email_repository import EmailRepository
from app.repositories.issue_repository import IssueRepository
from app.repositories.subscriber_repository import SubscriberRepository
from app.schemas.email import EmailBatchRead, EmailPreviewRead
from app.services.email_providers.base import EmailMessage, EmailProvider
from app.services.email_providers.registry import get_email_provider
from app.services.email_renderer import DailyYorkerEmailRenderer


class EmailIssueNotFoundError(Exception):
    pass


class EmailConfigurationError(Exception):
    pass


class EmailService:
    def __init__(
        self,
        provider: EmailProvider | None = None,
        renderer: DailyYorkerEmailRenderer | None = None,
        *,
        resend_api_key: str | None = None,
        email_from: str | None = None,
        public_site_url: str | None = None,
        email_reply_to: str | None = None,
        safety_dry_run: bool | None = None,
    ):
        self.provider = provider
        self.renderer = renderer or DailyYorkerEmailRenderer()
        self.resend_api_key = (
            resend_api_key if resend_api_key is not None else settings.resend_api_key
        )
        self.email_from = email_from or settings.email_from
        self.public_site_url = (public_site_url or settings.public_site_url).rstrip("/")
        self.email_reply_to = (
            email_reply_to if email_reply_to is not None else settings.email_reply_to
        )
        self.safety_dry_run = (
            safety_dry_run
            if safety_dry_run is not None
            else settings.email_dry_run
        )

    def preview_latest(self, db: Session) -> EmailPreviewRead:
        issue = self._get_latest_published_issue(db)
        return self._preview(db, issue, force=False)

    def send_latest(
        self,
        db: Session,
        *,
        dry_run: bool = True,
        force: bool = False,
    ) -> EmailBatchRead:
        issue = self._get_latest_published_issue(db)
        return self._send(db, issue, dry_run=dry_run, force=force)

    def send_issue(
        self,
        db: Session,
        issue_date: date,
        *,
        dry_run: bool = True,
        force: bool = False,
    ) -> EmailBatchRead:
        issue = IssueRepository(db).get_published_issue_by_date(issue_date)
        if issue is None:
            raise EmailIssueNotFoundError("Published issue not found.")
        return self._send(db, issue, dry_run=dry_run, force=force)

    def get_unsubscribe_subscriber(
        self,
        db: Session,
        raw_token: str,
    ) -> SubscriberModel | None:
        token = EmailRepository(db).get_unsubscribe_token(raw_token)
        if token is None:
            return None
        return db.get(SubscriberModel, token.subscriber_id)

    def unsubscribe(
        self,
        db: Session,
        raw_token: str,
    ) -> SubscriberModel | None:
        repository = EmailRepository(db)
        token = repository.get_unsubscribe_token(raw_token)
        if token is None:
            return None
        return repository.mark_unsubscribed(token)

    def _preview(
        self,
        db: Session,
        issue: IssueModel,
        force: bool,
    ) -> EmailPreviewRead:
        eligible, skipped_count = self._eligible_subscribers(db, issue, force)
        rendered = self._render_preview(db, issue)
        return EmailPreviewRead(
            subject=rendered.subject,
            html_preview=rendered.html,
            text_preview=rendered.text,
            issue_date=rendered.issue_date,
            would_send_count=len(eligible),
            skipped_count=skipped_count,
            dry_run=True,
        )

    def _send(
        self,
        db: Session,
        issue: IssueModel,
        *,
        dry_run: bool,
        force: bool,
    ) -> EmailBatchRead:
        eligible, skipped_count = self._eligible_subscribers(db, issue, force)
        preview = self._render_preview(db, issue)
        effective_dry_run = dry_run or self.safety_dry_run

        if effective_dry_run:
            return EmailBatchRead(
                subject=preview.subject,
                html_preview=preview.html,
                text_preview=preview.text,
                issue_date=preview.issue_date,
                would_send_count=len(eligible),
                skipped_count=skipped_count,
                dry_run=True,
                sent_count=0,
                failed_count=0,
            )

        if not self.resend_api_key:
            raise EmailConfigurationError(
                "RESEND_API_KEY is required when real email delivery is enabled."
            )

        provider = self.provider or get_email_provider(self.resend_api_key)
        repository = EmailRepository(db)
        issue_schema = IssueRepository(db).to_read_schema(issue)
        sent_count = 0
        failed_count = 0

        for subscriber in eligible:
            attempt_number = repository.next_attempt_number(issue.id, subscriber.id)
            raw_token = repository.create_unsubscribe_token(subscriber.id)
            delivery = repository.create_pending_delivery(
                issue,
                subscriber,
                provider.name,
                attempt_number,
            )
            unsubscribe_url = f"{self.public_site_url}/unsubscribe/{raw_token}"

            try:
                rendered = self.renderer.render(
                    issue_schema,
                    self.public_site_url,
                    unsubscribe_url,
                )
                result = provider.send(
                    EmailMessage(
                        to_email=subscriber.email,
                        from_email=self.email_from,
                        reply_to=self.email_reply_to,
                        subject=rendered.subject,
                        html=rendered.html,
                        text=rendered.text,
                        headers={
                            "List-Unsubscribe": f"<{unsubscribe_url}>",
                            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                        },
                        idempotency_key=(
                            f"outside-edge-issue-{issue.id}-subscriber-"
                            f"{subscriber.id}-attempt-{attempt_number}"
                        ),
                    )
                )
                repository.mark_sent(delivery, result.provider_message_id)
                sent_count += 1
            except Exception as exc:
                safe_message = str(exc).replace(raw_token, "[redacted]")
                repository.mark_failed(delivery, safe_message)
                failed_count += 1

        return EmailBatchRead(
            subject=preview.subject,
            html_preview=preview.html,
            text_preview=preview.text,
            issue_date=preview.issue_date,
            would_send_count=len(eligible),
            skipped_count=skipped_count,
            dry_run=False,
            sent_count=sent_count,
            failed_count=failed_count,
        )

    def _eligible_subscribers(
        self,
        db: Session,
        issue: IssueModel,
        force: bool,
    ) -> tuple[list[SubscriberModel], int]:
        subscribers = SubscriberRepository(db).get_all_subscribers()
        email_repository = EmailRepository(db)
        eligible: list[SubscriberModel] = []
        skipped_count = 0

        for subscriber in subscribers:
            if not subscriber.is_active:
                skipped_count += 1
                continue
            if not force and email_repository.has_blocking_delivery(
                issue.id,
                subscriber.id,
            ):
                skipped_count += 1
                continue
            eligible.append(subscriber)

        return eligible, skipped_count

    def _render_preview(self, db: Session, issue: IssueModel):
        issue_schema = IssueRepository(db).to_read_schema(issue)
        return self.renderer.render(
            issue_schema,
            self.public_site_url,
            f"{self.public_site_url}/unsubscribe/preview-token",
        )

    def _get_latest_published_issue(self, db: Session) -> IssueModel:
        issues = IssueRepository(db).get_published_issues(limit=1)
        if not issues:
            raise EmailIssueNotFoundError("No published issue is available.")
        return issues[0]
