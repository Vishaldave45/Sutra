from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.errors import NotFoundError, ValidationError
from apps.api.db.models.conversation import Conversation, Message, MessageRole
from apps.api.repositories.conversation import ConversationRepository
from apps.api.repositories.message import MessageRepository


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._conv_repo = ConversationRepository(session)
        self._msg_repo = MessageRepository(session)

    async def create_conversation(
        self, metadata: dict[str, Any] | None = None
    ) -> Conversation:
        return await self._conv_repo.create(metadata=metadata)

    async def get_conversation(self, conversation_id: UUID) -> Conversation:
        conversation = await self._conv_repo.get_by_id(conversation_id)
        if conversation is None:
            raise NotFoundError(f"Conversation '{conversation_id}' not found")
        return conversation

    async def list_conversations(
        self, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return await self._conv_repo.list(limit=safe_limit, offset=safe_offset)

    async def create_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        if not content or not content.strip():
            raise ValidationError("Message content cannot be empty or whitespace only")

        exists = await self._conv_repo.exists(conversation_id)
        if not exists:
            raise NotFoundError(f"Conversation '{conversation_id}' not found")

        return await self._msg_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content.strip(),
            metadata=metadata,
        )

    async def list_messages(
        self,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Message]:
        exists = await self._conv_repo.exists(conversation_id)
        if not exists:
            raise NotFoundError(f"Conversation '{conversation_id}' not found")

        safe_limit = max(1, min(limit, 200))
        safe_offset = max(0, offset)
        return await self._msg_repo.list_by_conversation(
            conversation_id=conversation_id,
            limit=safe_limit,
            offset=safe_offset,
        )
