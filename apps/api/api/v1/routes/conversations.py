from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from apps.api.dependencies import get_conversation_service
from apps.api.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    MessageCreate,
    MessageRead,
)
from apps.api.services.conversation import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post(
    "",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversation",
)
async def create_conversation(
    payload: ConversationCreate | None = None,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationRead:
    metadata = payload.metadata if payload else None
    conversation = await service.create_conversation(metadata=metadata)
    return ConversationRead.model_validate(conversation)


@router.get(
    "",
    response_model=list[ConversationRead],
    summary="List conversations",
)
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationRead]:
    conversations = await service.list_conversations(limit=limit, offset=offset)
    return [ConversationRead.model_validate(c) for c in conversations]


@router.get(
    "/{conversation_id}",
    response_model=ConversationRead,
    summary="Get conversation by ID",
)
async def get_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationRead:
    conversation = await service.get_conversation(conversation_id)
    return ConversationRead.model_validate(conversation)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create message in conversation",
)
async def create_message(
    conversation_id: UUID,
    payload: MessageCreate,
    service: ConversationService = Depends(get_conversation_service),
) -> MessageRead:
    message = await service.create_message(
        conversation_id=conversation_id,
        role=payload.role,
        content=payload.content,
        metadata=payload.metadata,
    )
    return MessageRead.model_validate(message)


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageRead],
    summary="List messages in conversation",
)
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ConversationService = Depends(get_conversation_service),
) -> list[MessageRead]:
    messages = await service.list_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )
    return [MessageRead.model_validate(m) for m in messages]

