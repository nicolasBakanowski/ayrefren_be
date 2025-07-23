def test_add_work_order_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/parts/",
        json={
            "work_order_id": 999,
            "quantity": 1,
            "name": "Test Part",
            "unit_price": 10,
            "subtotal": 10,
            "increment_per_unit": 20,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404
