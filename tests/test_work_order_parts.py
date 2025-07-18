def test_add_part_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/parts/",
        json={
            "work_order_id": 999,
            "part_id": 999,
            "quantity": 1,
            "unit_price": 10,
            "subtotal": 10,
            "increment_per_unit": 20,
        },
    )
    assert resp.status_code == 404
