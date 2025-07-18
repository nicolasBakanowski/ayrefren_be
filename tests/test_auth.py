import asyncio
from app.models.users import Role
from app.services.auth import AuthService
from app.schemas.users import UserCreate
from app.db.repositories.users import UsersRepository
from app.core.security import verify_password


def test_authenticate_and_login_token(client):
    _, session_factory = client

    async def seed_user():
        async with session_factory() as session:
            role = Role(name="auth")
            session.add(role)
            await session.commit()
            await session.refresh(role)
            repo = UsersRepository(session)
            user = await repo.create(UserCreate(name="Auth", email="auth@example.com", password="secret", role_id=role.id))
            return user.email

    email = asyncio.run(seed_user())

    async def run():
        async with session_factory() as session:
            service = AuthService(session)
            user = await service.authenticate_user(email, "secret")
            token = service.login_token(user)
            return user.email, verify_password("secret", user.password), token

    user_email, valid_pw, token = asyncio.run(run())
    assert user_email == email
    assert valid_pw
    assert isinstance(token, str) and token

