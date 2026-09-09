from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.api.config import settings
from apps.api.db.models.conversation import Conversation, Message
from apps.api.main import app


@pytest.mark.asyncio
async def test_create_and_retrieve_conversation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        create_res = await client.post(
            "/api/v1/conversations",
            json={"metadata": {"source": "test", "channel": "api"}},
        )
        assert create_res.status_code == 201
        data = create_res.json()
        conv_id = data["id"]
        assert conv_id is not None
        assert data["metadata"] == {"source": "test", "channel": "api"}
        assert "created_at" in data
        assert "updated_at" in data

        # Retrieve
        get_res = await client.get(f"/api/v1/conversations/{conv_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["id"] == conv_id
        assert get_data["metadata"] == {"source": "test", "channel": "api"}


@pytest.mark.asyncio
async def test_list_conversations() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create two conversations
        res1 = await client.post("/api/v1/conversations", json={"metadata": {"tag": "1"}})
        res2 = await client.post("/api/v1/conversations", json={"metadata": {"tag": "2"}})
        assert res1.status_code == 201
        assert res2.status_code == 201

        list_res = await client.get("/api/v1/conversations?limit=10&offset=0")
        assert list_res.status_code == 200
        items = list_res.json()
        assert isinstance(items, list)
        assert len(items) >= 2
        ids = [item["id"] for item in items]
        assert res1.json()["id"] in ids
        assert res2.json()["id"] in ids


@pytest.mark.asyncio
async def test_get_nonexistent_conversation_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        missing_id = str(uuid4())
        res = await client.get(f"/api/v1/conversations/{missing_id}")
        assert res.status_code == 404
        assert "not found" in res.json()["error"].lower()


@pytest.mark.asyncio
async def test_create_messages_with_valid_roles() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create conversation
        conv_res = await client.post("/api/v1/conversations", json={})
        assert conv_res.status_code == 201
        conv_id = conv_res.json()["id"]

        # 1. System message
        msg_sys = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "system", "content": "You are Sutra OS.", "metadata": {"origin": "init"}},
        )
        assert msg_sys.status_code == 201
        sys_data = msg_sys.json()
        assert sys_data["role"] == "system"
        assert sys_data["content"] == "You are Sutra OS."
        assert sys_data["conversation_id"] == conv_id

        # 2. User message
        msg_user = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "user", "content": "Hello world!"},
        )
        assert msg_user.status_code == 201
        user_data = msg_user.json()
        assert user_data["role"] == "user"
        assert user_data["content"] == "Hello world!"

        # 3. Assistant message
        msg_ast = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "assistant", "content": "Greetings. How can I assist you today?"},
        )
        assert msg_ast.status_code == 201
        ast_data = msg_ast.json()
        assert ast_data["role"] == "assistant"
        assert ast_data["content"] == "Greetings. How can I assist you today?"


@pytest.mark.asyncio
async def test_create_message_invalid_role() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        conv_res = await client.post("/api/v1/conversations", json={})
        conv_id = conv_res.json()["id"]

        res = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "tool", "content": "Tool output"},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_message_empty_or_whitespace_content() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        conv_res = await client.post("/api/v1/conversations", json={})
        conv_id = conv_res.json()["id"]

        # Empty string
        res_empty = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "user", "content": ""},
        )
        assert res_empty.status_code == 422

        # Whitespace-only string
        res_ws = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "user", "content": "   \n\t  "},
        )
        assert res_ws.status_code == 422


@pytest.mark.asyncio
async def test_create_message_nonexistent_conversation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        missing_id = str(uuid4())
        res = await client.post(
            f"/api/v1/conversations/{missing_id}/messages",
            json={"role": "user", "content": "Hello?"},
        )
        assert res.status_code == 404
        assert "not found" in res.json()["error"].lower()


@pytest.mark.asyncio
async def test_message_chronological_ordering() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        conv_res = await client.post("/api/v1/conversations", json={})
        conv_id = conv_res.json()["id"]

        # Add sequential messages
        contents = ["Msg 1: System prompt", "Msg 2: User question", "Msg 3: Assistant answer"]
        roles = ["system", "user", "assistant"]

        for r, c in zip(roles, contents, strict=True):
            res = await client.post(
                f"/api/v1/conversations/{conv_id}/messages",
                json={"role": r, "content": c},
            )
            assert res.status_code == 201

        # Retrieve messages
        list_res = await client.get(f"/api/v1/conversations/{conv_id}/messages")
        assert list_res.status_code == 200
        messages = list_res.json()
        assert len(messages) == 3

        retrieved_contents = [m["content"] for m in messages]
        assert retrieved_contents == contents


@pytest.mark.asyncio
async def test_foreign_key_cascade_behavior() -> None:
    test_engine = create_async_engine(settings.database_url, future=True)
    session_maker = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        conv_res = await client.post("/api/v1/conversations", json={})
        conv_id = conv_res.json()["id"]

        msg_res = await client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"role": "user", "content": "Persistent message"},
        )
        msg_id = msg_res.json()["id"]

    # Delete conversation directly in database to test CASCADE
    async with session_maker() as session:
        conv = (
            await session.execute(
                select(Conversation).where(Conversation.id == conv_id)
            )
        ).scalar_one()
        await session.delete(conv)
        await session.commit()

    # Verify message was also deleted via CASCADE
    async with session_maker() as session:
        msg = (
            await session.execute(
                select(Message).where(Message.id == msg_id)
            )
        ).scalar_one_or_none()
        assert msg is None

    await test_engine.dispose()

