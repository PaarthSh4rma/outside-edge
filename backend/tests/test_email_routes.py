from tests.email_helpers import create_published_issue, create_subscriber


def test_send_latest_requires_admin_api_key(client):
    response = client.post("/admin/email/send-latest")

    assert response.status_code == 401


def test_preview_and_dry_run_return_rendered_email(client, db_session):
    create_published_issue(db_session)
    create_subscriber(db_session, "reader@example.com")
    headers = {"X-Admin-API-Key": "test-admin-key"}

    preview = client.post("/admin/email/preview-latest", headers=headers)
    dry_run = client.post("/admin/email/send-latest?dry_run=true", headers=headers)

    assert preview.status_code == 200
    assert dry_run.status_code == 200
    assert preview.json()["would_send_count"] == 1
    assert "Outside Edge" in preview.json()["html_preview"]
    assert "OUTSIDE EDGE" in preview.json()["text_preview"]
    assert dry_run.json()["dry_run"] is True
    assert dry_run.json()["sent_count"] == 0

    issue_date = preview.json()["issue_date"]
    dated = client.post(
        f"/admin/email/send-issue/{issue_date}?dry_run=true",
        headers=headers,
    )
    assert dated.status_code == 200
    assert dated.json()["issue_date"] == issue_date
