import asyncio

import pytest
from fastapi import HTTPException

from app.core.validators import exists_or_404, get_or_404, validate_foreign_keys
from app.models.clients import Client, ClientType
from app.models.users import Role


def test_get_or_404_success(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            cli = Client(type=ClientType.persona, name="John")
            session.add(cli)
            await session.commit()
            await session.refresh(cli)
            obj = await get_or_404(session, Client, cli.id, name="Cliente")
            return obj.id

    found_id = asyncio.run(run())
    assert found_id > 0


def test_get_or_404_negative_id(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            await get_or_404(session, Client, -1)

    with pytest.raises(HTTPException):
        asyncio.run(run())


def test_get_or_404_not_found(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            await get_or_404(session, Client, 999)

    with pytest.raises(HTTPException):
        asyncio.run(run())


def test_exists_or_404_success(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            role = Role(name="admin")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            result = await exists_or_404(session, Role, role.id)
            return result

    exists = asyncio.run(run())
    assert exists is True


def test_exists_or_404_invalid(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            await exists_or_404(session, Role, -5)

    with pytest.raises(HTTPException):
        asyncio.run(run())


def test_exists_or_404_not_found(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            await exists_or_404(session, Role, 123)

    with pytest.raises(HTTPException):
        asyncio.run(run())


def test_validate_foreign_keys_success(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            role = Role(name="user")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            await validate_foreign_keys(session, {Role: role.id, Client: None})
            return True

    assert asyncio.run(run()) is True


def test_validate_foreign_keys_failure(client):
    _, session_factory = client

    async def run():
        async with session_factory() as session:
            await validate_foreign_keys(session, {Role: 999})

    with pytest.raises(HTTPException):
        asyncio.run(run())
