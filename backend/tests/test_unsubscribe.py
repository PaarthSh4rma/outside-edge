from urllib.parse import urlparse

from app.models.email import UnsubscribeTokenModel
from app.repositories.email_repository import EmailRepository
from tests.email_helpers import (
    FakeEmailProvider,
    create_published_issue,
    create_subscriber,
    make_real_send_service,
)


def test_unsubscribe_token_deactivates_subscriber_idempotently(client, db_session):
    create_published_issue(db_session)
    subscriber = create_subscriber(db_session, "reader@example.com")
    provider = FakeEmailProvider()
    make_real_send_service(provider).send_latest(db_session, dry_run=False)

    unsubscribe_header = provider.messages[0].headers["List-Unsubscribe"]
    unsubscribe_url = unsubscribe_header.removeprefix("<").removesuffix(">")
    raw_token = urlparse(unsubscribe_url).path.rsplit("/", 1)[-1]
    stored_token = db_session.query(UnsubscribeTokenModel).one()

    assert stored_token.token_hash != raw_token
    assert stored_token.token_hash == EmailRepository.hash_token(raw_token)

    confirmation = client.get(f"/unsubscribe/{raw_token}")
    assert confirmation.status_code == 200
    db_session.refresh(subscriber)
    assert subscriber.is_active is True

    first = client.post(f"/unsubscribe/{raw_token}")
    second = client.post(f"/unsubscribe/{raw_token}")

    assert first.status_code == 200
    assert second.status_code == 200
    db_session.refresh(subscriber)
    assert subscriber.is_active is False
    db_session.refresh(stored_token)
    assert stored_token.used_at is not None
