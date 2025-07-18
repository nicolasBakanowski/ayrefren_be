def test_parts_crud_flow(client):
    http, _ = client
    resp = http.post(
        "/parts/",
        json={"name": "Bolt", "price": 5.0, "description": "A"},
    )
    assert resp.status_code == 200
    part = resp.json()
    part_id = part["id"]

    resp = http.get("/parts/")
    assert resp.status_code == 200
    assert any(p["id"] == part_id for p in resp.json())

    resp = http.get(f"/parts/{part_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Bolt"

    resp = http.put(f"/parts/{part_id}", json={"name": "Nut"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Nut"

    resp = http.delete(f"/parts/{part_id}")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Part deleted"

    resp = http.get(f"/parts/{part_id}")
    assert resp.status_code == 404
