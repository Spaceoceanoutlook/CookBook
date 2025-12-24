import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from cookbook.core.database import get_db
from cookbook.core.security import hash_password
from cookbook.main import app
from cookbook.models import Base, User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
def client(db):
    from cookbook.core import database

    async def override_get_db():
        yield db

    app.dependency_overrides[database.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db: AsyncSession):
    hashed_password = hash_password("test_password")
    user = User(email="test@example.com", name="test", password_hash=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture(scope="function")
async def auth_token(client: TestClient, test_user: User):
    login_data = {"username": "test@example.com", "password": "test_password"}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    token = token_data.get("access_token")
    assert token is not None, f"Токен не найден в ответе: {token_data}"
    return f"Bearer {token}"
