
def test_create_truck_invalid_client(client):
    http, _ = client
    resp = http.post(
        "/trucks/",
        json={
            "client_id": 999,
            "license_plate": "ABC123",
            "brand": "Ford",
            "model": "F-150",
            "year": 2020,
        },
    )
    assert resp.status_code == 404
