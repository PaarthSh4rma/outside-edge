def sync_scores(client):
    return client.post(
        "/admin/sync-scores",
        headers={"X-Admin-API-Key": "test-admin-key"},
    )


def test_admin_score_sync_requires_api_key(client):
    response = client.post("/admin/sync-scores")

    assert response.status_code == 401


def test_score_routes_return_expected_application_data(client):
    sync_response = sync_scores(client)

    assert sync_response.status_code == 200
    assert sync_response.json()["matches_created"] == 5

    live_response = client.get("/matches/live")
    upcoming_response = client.get("/matches/upcoming")
    recent_response = client.get("/matches/recent")

    assert live_response.status_code == 200
    assert upcoming_response.status_code == 200
    assert recent_response.status_code == 200
    assert len(live_response.json()) == 1
    assert len(upcoming_response.json()) == 2
    assert len(recent_response.json()) == 2

    live_match = live_response.json()[0]
    assert live_match["format"] == "Test"
    assert live_match["competition"]["name"] == "Border-Gavaskar Trophy"
    assert live_match["latest_score"]["home_score"][0]["runs"] == 287
    assert "provider" not in live_match
    assert "provider_match_id" not in live_match

    match_response = client.get(f"/matches/{live_match['id']}")
    assert match_response.status_code == 200
    assert match_response.json()["id"] == live_match["id"]


def test_score_sync_route_is_idempotent(client):
    first = sync_scores(client)
    second = sync_scores(client)

    assert first.json()["matches_created"] == 5
    assert second.json()["matches_created"] == 0
    assert second.json()["snapshots_created"] == 0
