import datetime
from typing import List
from app.repository.chat_repository import ChatRepository
from app.schema.chat_schema import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChoiceResponse,
    MessageResponse,
)
from app.model.chat_model import ChatCompletion, ChatMessage
from app.mapper.chat_mapper import ChatMapper
from app.mapper.conversation_mapper import ConversationMapper
import uuid
from loguru import logger
from app.schema.conversation_schema import ConversationResponse


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.chat_mapper = ChatMapper()
        self.conversation_mapper = ConversationMapper()

    async def handle_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        last_user_message = request.messages[-1].content
        logger.debug(f"TODO implement ai-agent response for this message: {last_user_message}")
        username = "admin"

        # Convert request to model
        entity = self.chat_mapper.to_model(request)
        
        if entity.completion_id:
            entity.completion_id = str(uuid.uuid4())
            entity.created_by = username
            entity.created_date = datetime.datetime.now()

        entity.last_updated_by = username
        entity.last_updated_date = datetime.datetime.now()

        # Save to database
        entity = await self.chat_repository.save(entity)

        # Convert model to response
        return self.chat_mapper.to_schema(entity)

    async def find(self, query: dict, page: int, limit: int, sort: dict, project: dict = None) -> List[ChatCompletionResponse]:
        logger.debug(f"BEGIN SERVICE: find for query: {query}, page: {page}, limit: {limit}, sort: {sort}, project: {project}")
        entities = await self.chat_repository.find(query, page, limit, sort, project)
        return self.chat_mapper.to_schema_list(entities)

    async def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletionResponse:
        entity = await self.chat_repository.find_by_id(completion_id, project)
        return self.chat_mapper.to_schema(entity) if entity else None

    async def find_messages(self, completion_id: str) -> List[ChatMessage]:
        return await self.chat_repository.find_messages(completion_id)

    # conversation service
    async def find_all_conversations(self, username: str) -> List[ConversationResponse]:
        """Find all conversations for a given username."""
        query = {"created_by": username}
        sort = {"last_updated_date": -1}  # Sort by last updated date in descending order

        entities = await self.chat_repository.find(query, page=1, limit=100, sort=sort)
        result = self.conversation_mapper.to_schema_list(entities)
        return ConversationResponse(items=result, total=len(result), limit=100, offset=0)



    async def find_conversation_by_id(self, completion_id: str) -> ConversationResponse:
        """Find a conversation by its completion ID."""
        entity = await self.chat_repository.find_by_id(completion_id)
        result = self.conversation_mapper.to_schema(entity) if entity else None
        return ConversationResponse(items=[result], total=1, limit=1, offset=0)
