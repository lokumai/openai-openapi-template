import datetime
from typing import List
from app.db.factory import db_client
from app.model.chat_model import ChatMessage, ChatCompletion
from loguru import logger
import uuid
import pymongo


class DocumentNotFoundError(Exception):
    """Raised when a document is not found in the database."""
    pass

# TODO: llm_model, llm_provider will come from .env file

class ChatRepository:
    def __init__(self):
        logger.info("Initializing ChatRepository")
        self.db = db_client.db
        self.collection = "chat_completion"

    async def _create(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Create a new chat completion in the database.

        Args:
            entity (ChatCompletion): The chat completion entity to create

        Returns:
            ChatCompletion: The created chat completion

        Raises:
            Exception: If the chat completion is not created
        """
        logger.info(f"Creating new chat completion for user: {entity.created_by}")
        
        entity.completion_id = str(uuid.uuid4()) if entity.completion_id is None else entity.completion_id
        entity_dict = entity.model_dump(by_alias=True) 

        # MongoDB'ye kaydet
        insert_result = await self.db.chat_completion.insert_one(entity_dict)
        
        if not insert_result.inserted_id:
            logger.error(f"Failed to create new chat completion with ID: {entity.completion_id}")
            raise Exception(f"Failed to create chat completion with ID: {entity.completion_id}")

        logger.info(f"Successfully created new chat completion with ID: {entity.completion_id}")
        return await self.find_by_id(entity.completion_id)

    async def _update(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Update an existing chat completion in the database.
        
        Args:
            entity (ChatCompletion): The chat completion entity to update
            
        Returns:
            ChatCompletion: The updated chat completion
            
        Raises:
            ValueError: If completion_id is not provided
            DocumentNotFoundError: If the document to update is not found
        """
        if not entity.completion_id:
            raise ValueError("Cannot update chat completion without completion_id")

        logger.info(f"Updating chat completion with ID: {entity.completion_id}")
        
        # these fields are not updatable
        non_updatable_fields = {"created_date", "created_by", "completion_id"}
        
        # get the model data and remove the non-updatable fields
        update_payload = {
            k: v for k, v in entity.model_dump(by_alias=True).items() 
            if k not in non_updatable_fields
        }
        
        if not update_payload:
            logger.warning(f"No updatable fields found for chat completion ID: {entity.completion_id}")
            return await self.find_by_id(entity.completion_id)
        
        query = {"completion_id": entity.completion_id}
        update = {"$set": update_payload}
        
        try:
            result = await self.db.chat_completion.update_one(query, update)
            
            if result.matched_count == 0:
                logger.error(f"Chat completion with ID {entity.completion_id} not found for update")
                raise DocumentNotFoundError(f"Chat completion with ID {entity.completion_id} not found")
                
            if result.modified_count == 0:
                logger.info(f"Chat completion with ID {entity.completion_id} matched but not modified")
            else:
                logger.info(f"Successfully updated chat completion with ID: {entity.completion_id}")
                
            return await self.find_by_id(entity.completion_id)
            
        except Exception as e:
            logger.error(f"Error updating chat completion with ID {entity.completion_id}: {str(e)}")
            raise

    async def save(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Save a chat completion to the database. If the chat completion has a completion_id,
        it will be updated. Otherwise, a new chat completion will be created.
        """
        logger.debug(f"BEGIN REPO: save chat completion. username: {entity.created_by}, completion_id: {entity.completion_id}")
        
        try:

            result = await self.find_by_id(entity.completion_id)
            if result:
                return await self._update(entity)
            else:
                return await self._create(entity)
        except Exception as e:
            logger.error(f"Error saving chat completion: {e}")
            raise
        finally:
            logger.debug("END REPO: save chat completion")

    async def find(
        self, query: dict = {}, page: int = 1, limit: int = 10, sort: dict = {"created_date": -1}, projection: dict = None
    ) -> List[ChatCompletion]:
        """
        Find a chat completion by a given query. with pagination
        Example : query = {"created_by": "admin"}
        """
        logger.debug(f"BEGIN REPO: find chat completion. query: {query}, page: {page}, limit: {limit}, sort: {sort}, projection: {projection}")
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        skip = (page - 1) * limit
        sort_query = sort if sort else [("created_date", pymongo.DESCENDING)]

        cursor = self.db.chat_completion.find(query, projection).skip(skip).limit(limit).sort(sort_query)
        db_docs = await cursor.to_list(length=limit)
        result_models = []
        for item in db_docs:
            try:
                result_models.append(ChatCompletion(**item))
            except Exception as e:
                logger.error(f"Error parsing ChatCompletion from DB for item with id {item.get('_id', 'N/A')}: {e}", exc_info=True)
                # TODO: handle error

        logger.trace(f"REPO find result (raw): {db_docs}")
        logger.trace(f"REPO find result (models): {result_models}")
        logger.debug(f"END REPO: find, returning {len(result_models)} models.")
        return result_models

    async def find_by_id(self, completion_id: str, projection: dict = None) -> ChatCompletion:
        """
        Find a chat completion by a given id.
        Example : completion_id = "123"
        """
        logger.debug(f"BEGIN REPO: find chat completion by id. input parameters: completion_id: {completion_id}, projection: {projection}")

        entity_doc = await self.db.chat_completion.find_one({"completion_id": completion_id}, projection)

        if entity_doc:
            logger.trace(f"REPO find_by_id. Found entity_doc: {entity_doc}")
            try:
                final_entity = ChatCompletion(**entity_doc)
                logger.debug(f"END REPO: find_by_id. Found: {final_entity.completion_id}")
                return final_entity
            except Exception as e:
                logger.error(f"Error parsing ChatCompletion from DB for id {completion_id}: {e}", exc_info=True)
                return None  # Parse hatası durumunda None döndür
        else:
            logger.info(f"Chat completion with ID {completion_id} not found in DB.")
            return None

    async def find_messages(self, completion_id: str) -> List[ChatMessage]:
        """
        Find all messages for a given chat completion id.
        Example : completion_id = "123"
        """
        logger.debug(f"BEGIN REPO: find messages for chat completion id. input parameters: completion_id: {completion_id}")
        projection = {"messages": 1, "_id": 0}
        chat_doc = await self.db.chat_completion.find_one({"completion_id": completion_id}, projection)

        if chat_doc and "messages" in chat_doc and chat_doc["messages"]:
            try:
                messages_list = [ChatMessage(**item) for item in chat_doc["messages"]]
                logger.debug(f"END REPO: find_messages. Found {len(messages_list)} messages.")
                return messages_list
            except Exception as e:
                logger.error(f"Error parsing messages for completion_id {completion_id}: {e}", exc_info=True)
                return []

        logger.info(f"No messages found for completion_id {completion_id} or messages field is empty/missing.")
        return []
