from sqlalchemy.orm import Session

from app.models.subscriber import SubscriberModel
from app.schemas.subscriber import SubscriberCreate


class SubscriberRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_reactivate(self, subscriber: SubscriberCreate) -> SubscriberModel:
        existing_subscriber = (
            self.db.query(SubscriberModel)
            .filter(SubscriberModel.email == subscriber.email.lower())
            .first()
        )

        if existing_subscriber:
            existing_subscriber.is_active = True
            existing_subscriber.name = subscriber.name or existing_subscriber.name

            self.db.commit()
            self.db.refresh(existing_subscriber)

            return existing_subscriber

        subscriber_model = SubscriberModel(
            email=subscriber.email.lower(),
            name=subscriber.name,
            is_active=True,
        )

        self.db.add(subscriber_model)
        self.db.commit()
        self.db.refresh(subscriber_model)

        return subscriber_model

    def get_active_subscribers(self) -> list[SubscriberModel]:
        return (
            self.db.query(SubscriberModel)
            .filter(SubscriberModel.is_active.is_(True))
            .order_by(SubscriberModel.created_at.desc())
            .all()
        )

    def get_all_subscribers(self) -> list[SubscriberModel]:
        return (
            self.db.query(SubscriberModel)
            .order_by(SubscriberModel.created_at.desc())
            .all()
        )
