import asyncio

from app.models.clients import Client, ClientType
from app.models.invoices import Invoice, InvoiceStatus, InvoiceType, PaymentMethod
from app.models.trucks import Truck
from app.models.work_orders import WorkOrder, WorkOrderStatus


def _seed_invoice(session_factory):
    async def run():
        async with session_factory() as session:
            client = Client(type=ClientType.persona, name="Payer")
            session.add(client)
            await session.flush()

            truck = Truck(client_id=client.id, license_plate="PAY111")
            status = WorkOrderStatus(name="open")
            session.add_all([truck, status])
            await session.flush()

            order = WorkOrder(truck_id=truck.id, status_id=status.id)
            inv_status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="A", surcharge=21)
            session.add_all([order, inv_status, inv_type])
            await session.flush()

            invoice = Invoice(
                work_order_id=order.id,
                client_id=client.id,
                invoice_type_id=inv_type.id,
                status_id=inv_status.id,
                labor_total=0,
                parts_total=0,
                iva=0,
                total=100,
            )
            method = PaymentMethod(name="Cash")
            session.add_all([invoice, method])
            await session.commit()
            await session.refresh(invoice)
            await session.refresh(method)
            return invoice.id, method.id

    return asyncio.run(run())


def _get_client_id(session_factory, invoice_id: int) -> int:
    async def run():
        async with session_factory() as session:
            invoice = await session.get(Invoice, invoice_id)
            return invoice.client_id

    return asyncio.run(run())


def test_list_payment_methods(client):
    http, session_factory = client

    async def seed():
        async with session_factory() as session:
            session.add(PaymentMethod(name="Cash"))
            await session.commit()

    asyncio.run(seed())

    resp = http.get("/invoices/payment-methods")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Cash"


def test_total_paid(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 40},
    )
    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 60},
    )

    resp = http.get(f"/invoices/payments/{invoice_id}/total")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 100


def test_partial_payments_different_methods(client):
    http, session_factory = client
    invoice_id, method1_id = _seed_invoice(session_factory)

    async def create_method():
        async with session_factory() as session:
            method = PaymentMethod(name="Card")
            session.add(method)
            await session.commit()
            await session.refresh(method)
            return method.id

    method2_id = asyncio.run(create_method())

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method1_id, "amount": 30},
    )
    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method2_id, "amount": 70},
    )

    resp = http.get(f"/invoices/payments/{invoice_id}")
    assert resp.status_code == 200
    payments = resp.json()["data"]
    assert len(payments) == 2
    assert {p["method_id"] for p in payments} == {method1_id, method2_id}

    resp = http.get(f"/invoices/{invoice_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["paid"] == 100

    resp = http.get(f"/invoices/payments/{invoice_id}/total")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 100


def test_invoice_detail_surcharge(client):
    http, session_factory = client
    invoice_id, _ = _seed_invoice(session_factory)

    resp = http.get(f"/invoices/{invoice_id}/detail")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_without_surcharge"] == 100
    assert data["total_with_surcharge"] == 121


def test_exchange_bank_check(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)
    resp = http.post(
        "/invoices/payments/",
        json={
            "invoice_id": invoice_id,
            "method_id": method_id,
            "amount": 100,
            "bank_checks": [
                {
                    "bank_name": "BN",
                    "check_number": "123",
                    "amount": 100,
                    "type": "physical",
                    "due_date": "2023-01-01T00:00:00",
                }
            ],
        },
    )
    assert resp.status_code == 200
    check_id = resp.json()["data"]["bank_checks"][0]["id"]

    resp = http.post(
        f"/invoices/bank-checks/{check_id}/exchange",
        json={"exchange_date": "2023-01-10T00:00:00"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["exchange_date"].startswith("2023-01-10")


def test_list_payments_by_client(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)
    client_id = _get_client_id(session_factory, invoice_id)

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 50},
    )

    resp = http.get("/invoices/payments/", params={"client_id": client_id})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["invoice_id"] == invoice_id


def test_list_payments_by_invoice_query(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 80},
    )

    resp = http.get("/invoices/payments/", params={"invoice_id": invoice_id})
    assert resp.status_code == 200
    payments = resp.json()["data"]
    assert len(payments) == 1
    assert payments[0]["invoice_id"] == invoice_id


def test_list_payments_pagination(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    for amount in [10, 20, 30]:
        http.post(
            "/invoices/payments/",
            json={"invoice_id": invoice_id, "method_id": method_id, "amount": amount},
        )

    resp = http.get(
        "/invoices/payments/", params={"invoice_id": invoice_id, "skip": 1, "limit": 1}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["amount"] == 20


def test_list_payments_by_invoice_pagination(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    for amount in [5, 15]:
        http.post(
            "/invoices/payments/",
            json={"invoice_id": invoice_id, "method_id": method_id, "amount": amount},
        )

    resp = http.get(f"/invoices/payments/{invoice_id}", params={"skip": 1, "limit": 1})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["amount"] == 15


def test_search_payments_includes_invoice_and_client(client):
    http, session_factory = client
    invoice_id, method_id = _seed_invoice(session_factory)

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_id, "amount": 50},
    )

    resp = http.get("/invoices/payments/")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    payment = data[0]
    assert "invoice" in payment
    invoice = payment["invoice"]
    expected_keys = {
        "id",
        "work_order_id",
        "client_id",
        "invoice_type_id",
        "status_id",
        "labor_total",
        "parts_total",
        "iva",
        "total",
        "invoice_number",
        "issued_at",
        "paid",
        "accepted",
        "client",
        "status",
        "invoice_type",
    }
    assert set(invoice.keys()) == expected_keys
    assert invoice["client"]["name"] == "Payer"


def test_list_payments_by_type(client):
    http, session_factory = client
    invoice_id, method_cash_id = _seed_invoice(session_factory)

    async def create_card_method():
        async with session_factory() as session:
            method = PaymentMethod(name="Card")
            session.add(method)
            await session.commit()
            await session.refresh(method)
            return method.id

    method_card_id = asyncio.run(create_card_method())

    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_cash_id, "amount": 10},
    )
    http.post(
        "/invoices/payments/",
        json={"invoice_id": invoice_id, "method_id": method_card_id, "amount": 20},
    )

    resp = http.get("/invoices/payments/", params={"type": "Cash"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["method"]["name"] == "Cash"


def test_list_payments_by_check_type(client):
    http, session_factory = client
    invoice_id, _ = _seed_invoice(session_factory)

    async def create_cheque_method():
        async with session_factory() as session:
            method = PaymentMethod(name="Cheque")
            session.add(method)
            await session.commit()
            await session.refresh(method)
            return method.id

    cheque_method_id = asyncio.run(create_cheque_method())

    http.post(
        "/invoices/payments/",
        json={
            "invoice_id": invoice_id,
            "method_id": cheque_method_id,
            "amount": 100,
            "bank_checks": [
                {
                    "bank_name": "BN",
                    "check_number": "123",
                    "amount": 100,
                    "type": "physical",
                    "due_date": "2023-01-01T00:00:00",
                }
            ],
        },
    )
    http.post(
        "/invoices/payments/",
        json={
            "invoice_id": invoice_id,
            "method_id": cheque_method_id,
            "amount": 100,
            "bank_checks": [
                {
                    "bank_name": "BN",
                    "check_number": "124",
                    "amount": 100,
                    "type": "electronic",
                    "due_date": "2023-01-01T00:00:00",
                }
            ],
        },
    )

    resp = http.get("/invoices/payments/", params={"type": "physical"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["bank_checks"][0]["type"] == "physical"
