def test_add_task_invalid_fk(client):
    http, _ = client
    resp = http.post(
        "/work-orders/tasks/",
        json={"work_order_id": 999, "user_id": 999, "area_id": 999, "description": "", "price": 0},
    )
    assert resp.status_code == 404
