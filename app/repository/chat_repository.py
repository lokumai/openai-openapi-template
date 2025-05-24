from typing import List
from app.db.factory import db_client
from app.model.chat_model import ChatMessage, ChatCompletion
from loguru import logger
import uuid


class ChatRepository:
    def __init__(self):
        logger.info("Initializing ChatRepository")
        self.db = db_client.db
        self.collection = "chat_completion"

    def save(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Upsert a chat completion into the database. If the chat completion already exists, it will be updated. If it does not exist, it will be created.
        """
        logger.debug(f"BEGIN: save chat completion. input data: {entity.model_dump()}")
        if entity.completion_id is None:
            logger.warning("completion_id is None. Generating a new one")
        else:
            logger.debug(f"completion_id is not None. Using the existing one: {entity.completion_id}")

        query = {"completion_id": entity.completion_id}
        update = {"$set": entity.model_dump()}

        upserted_entity = self.db.chat_completion.update_one(query, update, upsert=True)
        logger.debug(f"upserted_entity: {upserted_entity}")

        completion_id = entity.completion_id if entity.completion_id else str(uuid.uuid4())
        entity.completion_id = completion_id

        # save conversation if new chat completion
        # TODO: save conversation

        result = self.find_by_id(completion_id)
        logger.debug("END: save chat completion")
        return result

    def find(self, query: dict = {}, page: int = 1, limit: int = 10, sort: dict = {"created_date": -1}, project: dict = None) -> List[ChatCompletion]:
        """
        Find a chat completion by a given query. with pagination
        Example : query = {"created_by": "admin"}
        """
        logger.debug(f"BEGIN: find chat completion. input parameters: query: {query}, page: {page}, limit: {limit}, sort: {sort}, project: {project}")
        skip = (page - 1) * limit
        sort = sort if sort else {"created_date": -1}

        result = self.db.chat_completion.find(query, project).skip(skip).limit(limit).sort(sort)
        logger.debug(f"result: {result}")
        result = [ChatCompletion(**item) for item in result]
        logger.debug("END: find chat completion")
        return result

    def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletion:
        """
        Find a chat completion by a given id.
        Example : completion_id = "123"
        """
        logger.debug(f"BEGIN: find chat completion by id. input parameters: completion_id: {completion_id}, project: {project}")
        entity = self.db.chat_completion.find_one({"completion_id": completion_id}, project)
        result = ChatCompletion(**entity)
        logger.debug("END: find chat completion by id")
        return result

    def find_messages(self, completion_id: str) -> List[ChatMessage]:
        """
        Find all messages for a given chat completion id.
        Example : completion_id = "123"
        """
        # query = {"completion_id": completion_id}
        project = {"messages": 1}
        result = self.find_by_id(completion_id, project)
        return [ChatMessage(**item) for item in result["messages"]]
