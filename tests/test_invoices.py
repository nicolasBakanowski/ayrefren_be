import asyncio
from app.models.clients import Client, ClientType
from app.models.invoices import InvoiceStatus, InvoiceType


def test_create_invoice_invalid_order(client):
    http, session_factory = client
    async def setup_refs():
        async with session_factory() as session:
            client_obj = Client(type=ClientType.persona, name="Test")
            status = InvoiceStatus(name="pending")
            inv_type = InvoiceType(name="type1")
            session.add_all([client_obj, status, inv_type])
            await session.commit()
            await session.refresh(client_obj)
            await session.refresh(status)
            await session.refresh(inv_type)
            return client_obj.id, inv_type.id, status.id

    cli_id, inv_type_id, status_id = asyncio.run(setup_refs())
    resp = http.post(
        "/invoices/",
        json={
            "work_order_id": 123,
            "client_id": cli_id,
            "invoice_type_id": inv_type_id,
            "status_id": status_id,
            "labor_total": 0,
            "parts_total": 0,
            "iva": 0,
            "total": 0,
        },
    )
    assert resp.status_code == 404
