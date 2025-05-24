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
import uuid
from loguru import logger
from app.schema.conversation import ConversationResponse


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()

    async def handle_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        last_user_message = request.messages[-1].content
        response_content = f"TODO implement ai-agent response for this message: {last_user_message}"
        username = "admin"

        entity = ChatCompletion(**request.model_dump())
        if entity.completion_id:
            entity.completion_id = str(uuid.uuid4())
            entity.created_by = username
            entity.created_date = datetime.datetime.now()

        entity.last_updated_by = username
        entity.last_updated_date = datetime.datetime.now()

        entity = await self.chat_repository.save(entity)

        result = ChatCompletionResponse(**entity.model_dump())
        messages = [MessageResponse(**{"role": "assistant", "content": response_content})]  # TODO: implement ai-agent response
        result.choices = [
            ChoiceResponse(
                **{
                    "index": 0,
                    "message": messages[0],
                    "finish_reason": "stop",
                }
            )
        ]
        return result

    async def find(self, query: dict, page: int, limit: int, sort: dict, project: dict = None) -> List[ChatCompletionResponse]:
        logger.debug(f"BEGIN SERVICE: find for query: {query}, page: {page}, limit: {limit}, sort: {sort}, project: {project}")
        entities = await self.chat_repository.find(query, page, limit, sort, project)
        return [ChatCompletionResponse(**entity.model_dump()) for entity in entities]

    async def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletion:
        return await self.chat_repository.find_by_id(completion_id, project)

    async def find_messages(self, completion_id: str) -> List[ChatMessage]:
        return await self.chat_repository.find_messages(completion_id)

    # conversation service
    async def find_all_conversations(self, username: str) -> List[ConversationResponse]:
        raise NotImplementedError("Not implemented")

    async def find_conversation_by_id(self, completion_id: str) -> ConversationResponse:
        raise NotImplementedError("Not implemented")
