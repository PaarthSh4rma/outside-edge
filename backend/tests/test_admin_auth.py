def test_admin_route_rejects_missing_api_key(client):
    response = client.get("/admin/subscribers")

    assert response.status_code == 401


def test_admin_route_rejects_invalid_api_key(client):
    response = client.get(
        "/admin/subscribers",
        headers={"X-Admin-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_admin_route_accepts_valid_api_key(client):
    response = client.get(
        "/admin/subscribers",
        headers={"X-Admin-API-Key": "test-admin-key"},
    )

    assert response.status_code == 200
    assert response.json() == []
