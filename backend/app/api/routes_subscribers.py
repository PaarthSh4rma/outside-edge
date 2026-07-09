from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.subscriber_repository import SubscriberRepository
from app.schemas.subscriber import SubscriberCreate, SubscriberRead
from app.security import require_admin_api_key

public_router = APIRouter(prefix="/subscribers", tags=["subscribers"])
admin_router = APIRouter(
    prefix="/admin/subscribers",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)


@public_router.post("", response_model=SubscriberRead)
def create_subscriber(
    subscriber: SubscriberCreate,
    db: Session = Depends(get_db),
):
    subscriber_repository = SubscriberRepository(db)
    return subscriber_repository.create_or_reactivate(subscriber)


@admin_router.get("", response_model=list[SubscriberRead])
def get_subscribers(db: Session = Depends(get_db)):
    subscriber_repository = SubscriberRepository(db)
    return subscriber_repository.get_active_subscribers()
