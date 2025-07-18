def test_register_invalid_role(client):
    http, _ = client
    resp = http.post(
        "/users/register",
        json={
            "name": "x",
            "email": "x@example.com",
            "password": "x",
            "role_id": 999,
        },
    )
    assert resp.status_code == 404
