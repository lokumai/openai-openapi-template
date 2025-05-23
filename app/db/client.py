# mongodb client with motor and pymongo

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.db import db_config
from loguru import logger
from typing import Optional
from environs import Env

env = Env()
env.read_env()

DB_DATABASE_TYPE = env.str("DB_DATABASE_TYPE", "mongodb")


class MongoDBClient:
    _instance: Optional["MongoDBClient"] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db = None
    _is_connected: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(db_config.get_mongo_uri())
            self._db = self._client[db_config.DATABASE_NAME]

    @property
    def client(self) -> AsyncIOMotorClient:
        return self._client

    @property
    def db(self):
        return self._db

    async def connect(self):
        try:
            if not self._is_connected:
                if self._client is None:
                    self._client = AsyncIOMotorClient(db_config.get_mongo_uri())
                    self._db = self._client[db_config.DATABASE_NAME]
                await self._client.server_info()
                self._is_connected = True
                logger.info("Connected to MongoDB")
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        try:
            if self._is_connected and self._client is not None:
                self._client.close()
                self._client = None
                self._db = None
                self._is_connected = False
                logger.info("Disconnected from MongoDB")
        except Exception as e:
            logger.warning(f"Error while closing MongoDB connection: {e}")
            self._client = None
            self._db = None
            self._is_connected = False


# Global instance
mongodb = MongoDBClient()
