from typing import List
from app.db.client import MongoDBClient
from app.model.chat_model import ChatMessage, ChatCompletion


class ChatRepository:
    def __init__(self):
        self.db = MongoDBClient().db
        self.collection = "chat_completion"

    def save(self, entity: ChatCompletion) -> ChatCompletion:
        """
        Upsert a chat completion into the database. If the chat completion already exists, it will be updated. If it does not exist, it will be created.
        """
        query = {"completion_id": entity.completion_id}
        update = {"$set": entity.model_dump()}

        result = self.db.chat_completion.update_one(query, update, upsert=True)

        completion_id = str(result.upserted_id) if result.upserted_id else entity.completion_id
        entity.completion_id = completion_id

        # save conversation if new chat completion
        # TODO: save conversation

        return entity

    def find(self, query: dict, page: int = 1, limit: int = 10, sort: dict = None, project: dict = None) -> List[ChatCompletion]:
        """
        Find a chat completion by a given query. with pagination
        Example : query = {"created_by": "admin"}
        """
        
        skip = (page - 1) * limit
        sort = sort if sort else {"created_date": -1}

        result = self.db.chat_completion.find(query, project).skip(skip).limit(limit).sort(sort)
        return [ChatCompletion(**item) for item in result]

    def find_by_id(self, completion_id: str, project: dict = None) -> ChatCompletion:
        """
        Find a chat completion by a given id.
        Example : completion_id = "123"
        """
        result = self.db.chat_completion.find_one({"completion_id": completion_id}, project)
        return ChatCompletion(**result)

    def find_messages(self, completion_id: str) -> List[ChatMessage]:
        """
        Find all messages for a given chat completion id.
        Example : completion_id = "123"
        """
        #query = {"completion_id": completion_id}
        project = {"messages": 1}
        result = self.find_by_id(completion_id, project)
        return [ChatMessage(**item) for item in result["messages"]]
