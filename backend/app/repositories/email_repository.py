import hashlib
import secrets
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.email import EmailDeliveryModel, UnsubscribeTokenModel
from app.models.issue import IssueModel
from app.models.subscriber import SubscriberModel


class EmailRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_blocking_delivery(self, issue_id: int, subscriber_id: int) -> bool:
        return (
            self.db.query(EmailDeliveryModel)
            .filter(
                EmailDeliveryModel.issue_id == issue_id,
                EmailDeliveryModel.subscriber_id == subscriber_id,
                EmailDeliveryModel.status.in_(["pending", "sent", "delivered"]),
            )
            .first()
            is not None
        )

    def next_attempt_number(self, issue_id: int, subscriber_id: int) -> int:
        latest_attempt = (
            self.db.query(func.max(EmailDeliveryModel.attempt_number))
            .filter(
                EmailDeliveryModel.issue_id == issue_id,
                EmailDeliveryModel.subscriber_id == subscriber_id,
            )
            .scalar()
        )
        return (latest_attempt or 0) + 1

    def create_pending_delivery(
        self,
        issue: IssueModel,
        subscriber: SubscriberModel,
        provider: str,
        attempt_number: int,
    ) -> EmailDeliveryModel:
        delivery = EmailDeliveryModel(
            issue_id=issue.id,
            subscriber_id=subscriber.id,
            recipient_email=subscriber.email,
            provider=provider,
            status="pending",
            attempt_number=attempt_number,
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def mark_sent(
        self,
        delivery: EmailDeliveryModel,
        provider_message_id: str,
    ) -> None:
        delivery.status = "sent"
        delivery.provider_message_id = provider_message_id
        delivery.sent_at = datetime.now(UTC)
        delivery.error_message = None
        self.db.commit()

    def mark_failed(self, delivery: EmailDeliveryModel, error_message: str) -> None:
        delivery.status = "failed"
        delivery.error_message = error_message[:2000]
        self.db.commit()

    def create_unsubscribe_token(self, subscriber_id: int) -> str:
        raw_token = secrets.token_urlsafe(32)
        self.db.add(
            UnsubscribeTokenModel(
                subscriber_id=subscriber_id,
                token_hash=self.hash_token(raw_token),
            )
        )
        self.db.commit()
        return raw_token

    def get_unsubscribe_token(
        self,
        raw_token: str,
    ) -> UnsubscribeTokenModel | None:
        return (
            self.db.query(UnsubscribeTokenModel)
            .filter(UnsubscribeTokenModel.token_hash == self.hash_token(raw_token))
            .first()
        )

    def mark_unsubscribed(self, token: UnsubscribeTokenModel) -> SubscriberModel | None:
        subscriber = self.db.get(SubscriberModel, token.subscriber_id)
        if subscriber is None:
            return None

        subscriber.is_active = False
        if token.used_at is None:
            token.used_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(subscriber)
        return subscriber

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
