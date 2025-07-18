def test_assign_mechanic_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/mechanics/",
        json={"work_order_id": 999, "user_id": 999, "area_id": 999},
    )
    assert resp.status_code == 404
