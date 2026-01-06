"""
Test fixtures for Ferienhaus Kalender
"""
import os
import pytest
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test environment before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["PARTY_1_PASSWORD"] = "test1"
os.environ["PARTY_2_PASSWORD"] = "test2"
os.environ["PARTY_3_PASSWORD"] = "test3"
os.environ["PARTY_4_PASSWORD"] = "test4"
os.environ["ADMIN_PASSWORD"] = "admin123"
os.environ["SESSION_SECRET_KEY"] = "test-secret-key"

from database import Base, get_db
from main import app


# Create test engine and session
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False
)

test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests"""
    async with test_async_session_maker() as session:
        yield session


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables and provide a database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers_admin() -> dict[str, str]:
    """Get auth headers for admin user"""
    from auth import create_session_token, User

    user = User(party_id=None, is_admin=True, username="Admin")
    token = create_session_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_party1() -> dict[str, str]:
    """Get auth headers for party 1 user"""
    from auth import create_session_token, User

    user = User(party_id=1, is_admin=False, username="Siggi & Mausi")
    token = create_session_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_party2() -> dict[str, str]:
    """Get auth headers for party 2 user"""
    from auth import create_session_token, User

    user = User(party_id=2, is_admin=False, username="Silke & Wolfi & Zoe")
    token = create_session_token(user)
    return {"Authorization": f"Bearer {token}"}
