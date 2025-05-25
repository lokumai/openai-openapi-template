import datetime
from typing import Any, List

from app.agent.chat_agent_scheme import UserChatAgentRequest
from app.repository.chat_repository import ChatRepository
from app.schema.chat_schema import ChatCompletionRequest, ChatCompletionResponse, ChatMessageResponse, ChatMessageRequest
from app.mapper.chat_mapper import ChatMapper
from app.mapper.conversation_mapper import ConversationMapper
import uuid
from loguru import logger
from app.schema.conversation_schema import ConversationResponse
from app.service.chat_validation import ChatValidation
from app.agent.chat_agent_client import ChatAgentClient


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.chat_mapper = ChatMapper()
        self.conversation_mapper = ConversationMapper()
        self.chat_validation = ChatValidation()
        self.chat_agent_client = ChatAgentClient()

    async def find(self, query: dict, page: int, limit: int, sort: dict, project: dict = None) -> List[ChatCompletionResponse]:
        logger.debug(f"BEGIN SERVICE: find for query: {query}, page: {page}, limit: {limit}, sort: {sort}, project: {project}")
        entities = await self.chat_repository.find(query, page, limit, sort, project)
        return self.chat_mapper.to_schema_list(entities)

    async def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletionResponse:
        entity = await self.chat_repository.find_by_id(completion_id, project)
        return self.chat_mapper.to_schema(entity) if entity else None

    async def find_messages(self, completion_id: str) -> List[ChatMessageResponse]:
        logger.debug(f"BEGIN SERVICE: find_messages for completion_id: {completion_id}")
        messages = await self.chat_repository.find_messages(completion_id)
        logger.debug(f"END SERVICE: find_messages for completion_id: {completion_id}, messages: {len(messages)}")
        messages_response = [
            ChatMessageResponse(
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
    async def find_all_conversations(self, username: str) -> ConversationResponse:
        """Find all conversations for a given username."""
        query = {"created_by": username}
        sort = {"last_updated_date": -1}  # Sort by last updated date in descending order

        entities = await self.chat_repository.find(query, page=1, limit=100, sort=sort)
        result = self.conversation_mapper.to_schema_list(entities)
        return ConversationResponse(items=result, total=len(result), limit=100, offset=0)

    # conversation service
    async def find_conversation_by_id(self, completion_id: str) -> ConversationResponse | None:
        """Find a conversation by its completion ID."""
        logger.debug(f"BEGIN SERVICE: find_conversation_by_id for completion_id: {completion_id}")
        projection = {"messages": 0, "_id": 0}
        entity = await self.chat_repository.find_by_id(completion_id, projection=projection)
        logger.debug(f"END SERVICE: find_conversation_by_id for completion_id: {completion_id}, entity: {entity}")

        if entity:
            conversation_item = self.conversation_mapper.to_schema(entity)
            result = ConversationResponse(items=[conversation_item], total=1, limit=1, offset=0)
            return result
        else:
            return None

    async def find_plot_by_message(self, completion_id: str, message_id: str) -> dict[str, Any]:
        logger.debug(f"BEGIN SERVICE: find_plot_by_message for completion_id: {completion_id}, message_id: {message_id}")
        figure = await self.chat_repository.find_plot_by_message(completion_id, message_id)

        if figure:
            result = figure
        else:
            result = None
            logger.warning(f"END SERVICE: no figure found for completion_id: {completion_id}, message_id: {message_id}")

        logger.debug(f"END SERVICE: find_plot_by_message for completion_id: {completion_id}, message_id: {message_id} with figure")
        return result

    async def _save_chat_completion(self, chat_schema: ChatCompletionRequest, username: str) -> ChatCompletionResponse:
        """
        Save a chat completion to the database.
        """
        logger.debug("BEGIN SERVICE: Saving Chat Completion")
        try:
            # Convert request to model
            chat_model = self.chat_mapper.to_model(chat_schema)

            chat_model.last_updated_by = username
            chat_model.last_updated_date = datetime.datetime.now()
            if not chat_model.completion_id:
                # generate a new chat completion_id this is a new chat starting
                logger.info("Generating new chat completion_id for new chat starting")
                chat_model.completion_id = str(uuid.uuid4())

            # generate message_id and created_date for latest user message
            last_user_message_model = chat_model.messages[-1]
            last_user_message_model.message_id = str(uuid.uuid4())
            last_user_message_model.created_date = datetime.datetime.now()
            logger.debug(f"last_user_message_model: {last_user_message_model}")

            logger.debug(f"finding by id. entity: {chat_model.completion_id}")
            current_db_entity = await self.chat_repository.find_by_id(chat_model.completion_id)
            logger.debug(f"found by id. Current entity: {current_db_entity.completion_id if current_db_entity else 'None'}")

            # if chat completion is not found, create a new one
            if not current_db_entity:
                logger.info("Create new chat completion with new user request message")
                chat_model.created_by = username
                chat_model.created_date = datetime.datetime.now()
                chat_model.last_updated_by = username
                chat_model.last_updated_date = datetime.datetime.now()
                # title can generate with LLM from user request message.content
                chat_model.title = last_user_message_model.content[:20]

                final_entity = await self.chat_repository.create(chat_model)
            else:
                logger.info("Update existing chat completion with new user request message")

                logger.debug(f"before update. current db entity messsage count: {len(current_db_entity.messages)}")
                current_db_entity.messages.append(last_user_message_model)
                logger.debug(f"after update. current db entity messsage count: {len(current_db_entity.messages)}")
                current_db_entity.last_updated_date = datetime.datetime.now()
                final_entity = await self.chat_repository.update(current_db_entity)
                logger.debug(f"after update. final entity messsage count: {len(final_entity.messages)}")

            # Convert model to response
            result = self.chat_mapper.to_schema(final_entity, convert_last_message=True)
            logger.debug("END SERVICE")
            return result
        except Exception as e:
            logger.error(f"Error saving chat completion: {e}")
            raise

    async def chat_agent_client_process(self, user_chat_completion: ChatCompletionRequest, username: str):
        logger.debug(f"BEGIN SERVICE: Agentic Chat AI process. username: {username}")
        last_user_message = user_chat_completion.messages[-1].content
        user_chat_agent_request = UserChatAgentRequest(message=last_user_message)
        result = self.chat_agent_client.process(user_chat_agent_request)
        logger.debug("END SERVICE: Agentic Chat AI process")
        return result

    async def handle_chat_completion(self, user_chat_completion: ChatCompletionRequest, username: str) -> ChatCompletionResponse:
        last_user_message = user_chat_completion
        logger.debug(f"BEGIN SERVICE: last_user_message: {last_user_message}, username: {username}")

        # validate user message
        self.chat_validation.validate_request(user_chat_completion)

        # save user message to database
        logger.info("Saving user message to database")
        repo_user_message = await self._save_chat_completion(user_chat_completion, username)
        logger.info(f"Saved user message to database with completion_id: {repo_user_message.completion_id}")

        # region agentic-ai process start #########################################################
        try:
            logger.info("Agentic Chat AI process started")
            agent_result = await self.chat_agent_client_process(user_chat_completion, username)
            assistant_message = ChatMessageRequest(role="assistant", content=agent_result.message)
            assistant_chat_completion = user_chat_completion
            assistant_chat_completion.messages = [assistant_message]  # replace user messages with assistant message
            logger.info(f"Agentic Chat AI process completed. Part of Assistant Message...: {assistant_message.content[:50]}...")
        except Exception as e:
            logger.error(f"Error agentic-ai process: {e}")
            raise
        # endregion agentic-ai process start ######################################################

        # validate agent response
        self.chat_validation.validate_response(agent_result)

        # save assistant message to database
        repo_assistant_message = await self._save_chat_completion(assistant_chat_completion, username)

        # generate api response with user, agent, db etc... TBD
        result = repo_assistant_message

        logger.debug("END SERVICE")
        return result
