import pytest

from app.models.email import EmailDeliveryModel, UnsubscribeTokenModel
from app.repositories.issue_repository import IssueRepository
from app.services.email_service import EmailConfigurationError, EmailService
from app.services.issue_service import IssueService
from tests.email_helpers import (
    FakeEmailProvider,
    create_published_issue,
    create_subscriber,
    make_real_send_service,
)


def test_dry_run_does_not_call_provider_or_write_delivery_rows(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "reader@example.com")
    provider = FakeEmailProvider()

    result = make_real_send_service(provider).send_latest(db_session, dry_run=True)

    assert result.dry_run is True
    assert result.would_send_count == 1
    assert result.sent_count == 0
    assert provider.messages == []
    assert db_session.query(EmailDeliveryModel).count() == 0
    assert db_session.query(UnsubscribeTokenModel).count() == 0


def test_environment_safety_lock_keeps_explicit_send_in_dry_run(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "reader@example.com")
    provider = FakeEmailProvider()
    service = EmailService(
        provider=provider,
        resend_api_key="test-key-never-sent-to-resend",
        safety_dry_run=True,
    )

    result = service.send_latest(db_session, dry_run=False)

    assert result.dry_run is True
    assert provider.messages == []
    assert db_session.query(EmailDeliveryModel).count() == 0


def test_real_send_requires_resend_api_key(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "reader@example.com")
    provider = FakeEmailProvider()
    service = EmailService(
        provider=provider,
        resend_api_key="",
        safety_dry_run=False,
    )

    with pytest.raises(EmailConfigurationError):
        service.send_latest(db_session, dry_run=False)

    assert provider.messages == []
    assert db_session.query(EmailDeliveryModel).count() == 0


def test_successful_delivery_blocks_duplicate_unless_forced(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "reader@example.com")
    provider = FakeEmailProvider()
    service = make_real_send_service(provider)

    first = service.send_latest(db_session, dry_run=False)
    original_issue_id = db_session.query(EmailDeliveryModel).one().issue_id
    IssueService().generate_and_save_today_issue(db_session)
    regenerated_issue_id = IssueRepository(db_session).get_latest_issue().id
    duplicate = service.send_latest(db_session, dry_run=False)
    forced = service.send_latest(db_session, dry_run=False, force=True)

    assert first.sent_count == 1
    assert regenerated_issue_id == original_issue_id
    assert duplicate.sent_count == 0
    assert duplicate.skipped_count == 1
    assert forced.sent_count == 1
    assert len(provider.messages) == 2
    assert db_session.query(EmailDeliveryModel).count() == 2


def test_inactive_subscriber_is_counted_without_delivery_row(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "active@example.com")
    create_subscriber(db_session, "inactive@example.com", active=False)
    provider = FakeEmailProvider()

    result = make_real_send_service(provider).send_latest(
        db_session,
        dry_run=False,
    )

    assert result.sent_count == 1
    assert result.skipped_count == 1
    assert len(provider.messages) == 1
    assert db_session.query(EmailDeliveryModel).count() == 1


def test_provider_failure_does_not_stop_batch(db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "good@example.com")
    create_subscriber(db_session, "bad@example.com")
    provider = FakeEmailProvider(fail_for={"bad@example.com"})

    result = make_real_send_service(provider).send_latest(
        db_session,
        dry_run=False,
    )

    assert result.sent_count == 1
    assert result.failed_count == 1
    statuses = {
        delivery.recipient_email: delivery.status
        for delivery in db_session.query(EmailDeliveryModel).all()
    }
    assert statuses == {
        "good@example.com": "sent",
        "bad@example.com": "failed",
    }
