from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import Config
from alembic.script import ScriptDirectory
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from apps.api.config import Settings, settings
from apps.api.db.base import Base
from apps.api.db.session import get_db_session
from apps.api.main import app


def test_database_configuration_loads() -> None:
    test_settings = Settings(
        database_url="postgresql+psycopg://test_user:test_password@localhost:5444/test_db"
    )
    assert test_settings.database_url.startswith("postgresql+psycopg://")
    assert test_settings.database_url_sync.startswith("postgresql+psycopg://")


def test_declarative_base_instantiation() -> None:
    assert Base.metadata is not None


def test_alembic_scripts_configuration() -> None:
    alembic_cfg = Config("alembic.ini")
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    heads = script_dir.get_heads()
    assert len(heads) > 0


@pytest_asyncio.fixture
async def isolated_session() -> AsyncGenerator[AsyncSession, None]:
    test_engine = create_async_engine(settings.database_url, future=True)
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_database_connection_and_session_lifecycle(
    isolated_session: AsyncSession,
) -> None:
    result = await isolated_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session_dependency() -> None:
    generator = get_db_session()
    session = await anext(generator)
    assert isinstance(session, AsyncSession)
    result = await session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    with pytest.raises(StopAsyncIteration):
        await anext(generator)


@pytest.mark.asyncio
async def test_readiness_healthy() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/ready")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "sutra-api",
            "database": "ok",
        }


@pytest.mark.asyncio
async def test_readiness_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    bad_engine = create_async_engine(
        "postgresql+psycopg://invalid:invalid@127.0.0.1:54399/none"
    )
    bad_session_factory = async_sessionmaker(bind=bad_engine, class_=AsyncSession)
    monkeypatch.setattr(
        "apps.api.api.v1.routes.health.async_session_factory",
        bad_session_factory,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "degraded",
            "service": "sutra-api",
            "database": "unavailable",
        }
    await bad_engine.dispose()


def test_liveness_independent_of_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi.testclient import TestClient

    monkeypatch.setattr(
        "apps.api.api.v1.routes.health.async_session_factory",
        None,
    )
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sutra-api"}
