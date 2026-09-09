from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, metadata: dict[str, Any] | None = None) -> Conversation:
        conversation = Conversation(metadata_=metadata or {})
        self._session.add(conversation)
        await self._session.flush()
        await self._session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        result = await self._session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Conversation]:
        result = await self._session.execute(
            select(Conversation)
            .order_by(Conversation.created_at.desc(), Conversation.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def exists(self, conversation_id: UUID) -> bool:
        result = await self._session.execute(
            select(Conversation.id).where(Conversation.id == conversation_id)
        )
        return result.first() is not None
