import datetime
from typing import List
from app.db.factory import db_client
from app.model.chat_model import ChatMessage, ChatCompletion
from loguru import logger
import uuid
import pymongo


class ChatRepository:
    def __init__(self):
        logger.info("Initializing ChatRepository")
        self.db = db_client.db
        self.collection = "chat_completion"

    async def save(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Upsert a chat completion into the database. If the chat completion already exists, it will be updated. If it does not exist, it will be created.
        """
        logger.debug(f"BEGIN REPO: save chat completion. username: {entity.created_by}, completion_id: {entity.completion_id}")
        entity_dict = entity.model_dump(by_alias=True)
        if entity.completion_id is None:
            generated_completion_id = str(uuid.uuid4())
            logger.warning(f"completion_id was None. Generated a new one: {generated_completion_id}")
            entity.completion_id = generated_completion_id
            entity_dict["completion_id"] = generated_completion_id

            query = {"completion_id": generated_completion_id}
            update = {
                "$set": entity_dict,
                "$setOnInsert": {
                    "created_date": entity.created_date.isoformat()
                    if entity.created_date
                    else datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "created_by": entity.created_by,
                },
            }
        else:
            logger.debug(f"completion_id is not None. Using the existing one: {entity.completion_id}")
            query = {"completion_id": entity.completion_id}
            update_payload = entity_dict.copy()
            update_payload.pop("created_date", None)  # created_date is not updatable
            update_payload.pop("created_by", None)  # created_by is not updatable
            update_payload.pop("completion_id", None)  # completion_id is not updatable
            update = {"$set": update_payload}

        upsert_result = await self.db.chat_completion.update_one(query, update, upsert=True)
        logger.debug(f"upserted_entity. _id: {upsert_result.upserted_id}")

        if upsert_result.upserted_id:
            logger.info(f"Inserted new chat completion with ID: {entity.completion_id} (upserted_id: {upsert_result.upserted_id})")
        elif upsert_result.modified_count > 0:
            logger.info(f"Updated existing chat completion with ID: {entity.completion_id}")
        elif upsert_result.matched_count > 0:
            logger.info(f"Chat completion with ID: {entity.completion_id} matched but not modified.")
        else:
            logger.warning(
                f"Chat completion with ID: {entity.completion_id} - No operation performed (no match, no upsert, no modification). This might be unexpected."
            )

        # save conversation if new chat completion
        # TODO: save conversation

        # after upsert, find the final db entity. if is there any trigger, default, etc. return the latest one
        final_entity = await self.find_by_id(entity.completion_id)
        if not final_entity:
            # This should not happen, upsert should be successful.
            logger.error(f"CRITICAL: Failed to retrieve chat completion {entity.completion_id} immediately after save operation.")
            raise Exception(f"Data integrity issue: Could not find chat completion {entity.completion_id} after saving.")

        logger.debug(f"END REPO: save chat completion, returning final_entity_id: {final_entity.completion_id}")
        return final_entity

    async def find(
        self, query: dict = {}, page: int = 1, limit: int = 10, sort: dict = {"created_date": -1}, projection: dict = None
    ) -> List[ChatCompletion]:
        """
        Find a chat completion by a given query. with pagination
        Example : query = {"created_by": "admin"}
        """
        logger.debug(f"BEGIN REPO: find chat completion. query: {query}, page: {page}, limit: {limit}, sort: {sort}, projection: {projection}")
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
