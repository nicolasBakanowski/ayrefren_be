import asyncio

from app.models.users import Role


def test_register_invalid_role(client):
    http, _ = client
    resp = http.post(
        "/users/register",
        json={
            "name": "x",
            "email": "x@example.com",
            "password": "x",
            "role_id": 999,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["code"] == 404


def test_register_success(client):
    http, session_factory = client

    async def seed_role():
        async with session_factory() as session:
            role = Role(name="user")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            return role.id

    role_id = asyncio.run(seed_role())
    resp = http.post(
        "/users/register",
        json={
            "name": "John",
            "email": "john@example.com",
            "password": "secret",
            "role_id": role_id,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert data["data"]["email"] == "john@example.com"


def test_login_success(client):
    http, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role = Role(name="login")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            return http.post(
                "/users/register",
                json={
                    "name": "Log",
                    "email": "log@example.com",
                    "password": "pass",
                    "role_id": role.id,
                },
            ).json()["data"]

    user = asyncio.run(seed_user())
    resp = http.post(
        "/auth/login",
        data={"username": user["email"], "password": "pass"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_get_user_success(client):
    http, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role = Role(name="getter")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            resp = http.post(
                "/users/register",
                json={
                    "name": "Get",
                    "email": "get@example.com",
                    "password": "pwd",
                    "role_id": role.id,
                },
            )
            return resp.json()["data"]["id"], role.id

    user_id, _ = asyncio.run(seed_user())
    resp = http.get(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id


def test_list_users(client):
    http, session_factory = client

    async def seed_users():
        async with session_factory() as session:
            role = Role(name="lister")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            for i in range(2):
                http.post(
                    "/users/register",
                    json={
                        "name": f"U{i}",
                        "email": f"u{i}@example.com",
                        "password": "x",
                        "role_id": role.id,
                    },
                )
            return role.id

    role_id = asyncio.run(seed_users())
    resp = http.get(f"/users/?role_id={role_id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_user_success(client):
    http, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role1 = Role(name="old")
            role2 = Role(name="new")
            session.add_all([role1, role2])
            await session.commit()
            await session.refresh(role1)
            await session.refresh(role2)
            resp = http.post(
                "/users/register",
                json={
                    "name": "Old",
                    "email": "old@example.com",
                    "password": "oldpwd",
                    "role_id": role1.id,
                },
            )
            user = resp.json()["data"]
            return user["id"], role2.id

    user_id, new_role = asyncio.run(seed_user())
    resp = http.put(
        f"/users/{user_id}",
        json={
            "name": "Updated",
            "email": "new@example.com",
            "password": "newpwd",
            "role_id": new_role,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["role_id"] == new_role


def test_delete_user_success(client):
    http, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role = Role(name="deleter")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            user = http.post(
                "/users/register",
                json={
                    "name": "Del",
                    "email": "del@example.com",
                    "password": "pwd",
                    "role_id": role.id,
                },
            ).json()["data"]
            return user["id"]

    user_id = asyncio.run(seed_user())
    resp = http.delete(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["detail"]


def test_change_password(client):
    http, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role = Role(name="changer")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            user = http.post(
                "/users/register",
                json={
                    "name": "Ch",
                    "email": "ch@example.com",
                    "password": "old",
                    "role_id": role.id,
                },
            ).json()["data"]
            return user["id"], user["email"]

    user_id, email = asyncio.run(seed_user())
    resp = http.put(
        f"/users/{user_id}/password",
        json={"old_password": "old", "new_password": "new"},
    )
    assert resp.status_code == 200
    resp = http.post(
        "/auth/login",
        data={"username": email, "password": "new"},
    )
    assert resp.status_code == 200
