import datetime
from typing import Any, List, Optional
from app.repository.chat_repository import ChatRepository
from app.schema.chat_schema import ChatCompletionRequest, ChatCompletionResponse, MessageResponse
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

    async def find(self, query: dict, page: int, limit: int, sort: dict, project: dict = None) -> List[ChatCompletionResponse]:
        logger.debug(f"BEGIN SERVICE: find for query: {query}, page: {page}, limit: {limit}, sort: {sort}, project: {project}")
        entities = await self.chat_repository.find(query, page, limit, sort, project)
        return self.chat_mapper.to_schema_list(entities)

    async def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletionResponse:
        entity = await self.chat_repository.find_by_id(completion_id, project)
        return self.chat_mapper.to_schema(entity) if entity else None

    async def find_messages(self, completion_id: str) -> List[MessageResponse]:
        logger.debug(f"BEGIN SERVICE: find_messages for completion_id: {completion_id}")
        messages = await self.chat_repository.find_messages(completion_id)
        logger.debug(f"END SERVICE: find_messages for completion_id: {completion_id}, messages: {len(messages)}")
        messages_response = [
            MessageResponse(
                message_id=message.message_id,
                role=message.role,
                content=message.content,
                created_date=message.created_date,
                figure=(message.figure),
            )
            for message in messages
        ]
        return messages_response

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
        logger.debug(f"BEGIN SERVICE: find_conversation_by_id for completion_id: {completion_id}")
        projection = {"messages": 0, "_id": 0}
        entity = await self.chat_repository.find_by_id(completion_id, projection=projection)
        logger.debug(f"END SERVICE: find_conversation_by_id for completion_id: {completion_id}, entity: {entity}")

        if entity:
            # Tekil kayıt için doğrudan dönüşüm yapıyoruz
            result = self.conversation_mapper.to_schema(entity)
            return result
        else:
            return None

    async def find_plot_by_message(self, completion_id: str, message_id: str) -> Optional[dict[str, Any]]:
        logger.debug(f"BEGIN SERVICE: find_plot_by_message for completion_id: {completion_id}, message_id: {message_id}")
        figure = await self.chat_repository.find_plot_by_message(completion_id, message_id)

        if figure:
            result = figure
        else:
            result = None
            logger.warning(f"END SERVICE: no figure found for completion_id: {completion_id}, message_id: {message_id}")

        logger.debug(f"END SERVICE: find_plot_by_message for completion_id: {completion_id}, message_id: {message_id} with figure")
        return result




    async def handle_chat_completion(self, request: ChatCompletionRequest, username: str) -> ChatCompletionResponse:
        last_user_message = request.messages[-1].content
        logger.debug(f"TODO implement ai-agent response for this message: {last_user_message}")

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