import asyncio
from datetime import date

from app.models.expense import ExpenseType


def seed_expense_type(session_factory):
    async def run():
        async with session_factory() as session:
            et = ExpenseType(name="Alquiler")
            session.add(et)
            await session.commit()
            await session.refresh(et)
            return et.id

    return asyncio.run(run())


def test_create_and_list_expenses(client):
    http, session_factory = client
    type_id = seed_expense_type(session_factory)

    resp = http.post(
        "/expenses",
        json={
            "date": str(date(2024, 1, 1)),
            "amount": "10.50",
            "expense_type_id": type_id,
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["expense_type"]["id"] == type_id

    resp = http.get("/expense-types")
    assert resp.status_code == 200
    assert any(t["id"] == type_id for t in resp.json()["data"])

    resp = http.get("/expenses")
    assert resp.status_code == 200
    assert any(e["id"] == data["id"] for e in resp.json()["data"])


def test_invalid_expense_type(client):
    http, _ = client
    resp = http.post(
        "/expenses",
        json={"date": str(date(2024, 1, 1)), "amount": "5.00", "expense_type_id": 999},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert not body["success"]
    assert body["code"] == 404
