import asyncio


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


def test_truck_crud_flow(client):
    http, session_factory = client

    async def seed_client():
        async with session_factory() as session:
            from app.models.clients import Client, ClientType

            cli = Client(type=ClientType.persona, name="Acme")
            session.add(cli)
            await session.commit()
            await session.refresh(cli)
            return cli.id

    client_id = asyncio.run(seed_client())

    resp = http.post(
        "/trucks/",
        json={
            "client_id": client_id,
            "license_plate": "XYZ123",
            "brand": "Volvo",
            "model": "FH",
            "year": 2024,
        },
    )
    assert resp.status_code == 200
    truck_id = resp.json()["id"]

    resp = http.get("/trucks/")
    assert resp.status_code == 200
    assert any(t["id"] == truck_id for t in resp.json())

    resp = http.get(f"/trucks/{truck_id}")
    assert resp.status_code == 200
    assert resp.json()["license_plate"] == "XYZ123"

    resp = http.put(
        f"/trucks/{truck_id}",
        json={"brand": "Scania"},
    )
    assert resp.status_code == 200
    assert resp.json()["brand"] == "Scania"

    resp = http.delete(f"/trucks/{truck_id}")
    assert resp.status_code == 204
