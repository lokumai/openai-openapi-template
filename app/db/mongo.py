from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.db import db_config
from loguru import logger
from app.db.client import DatabaseClient


class PersistentMongoClient(DatabaseClient):
    """Real MongoDB client implementation"""

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._is_connected: bool = False

    @property
    def client(self) -> AsyncIOMotorClient:
        logger.info("Getting PersistentMongoClient")

        if not self._client:
            logger.info("Generating PersistentMongoClient")
            self._client = AsyncIOMotorClient(db_config.get_mongo_uri())
            self._db = self._client[db_config.DATABASE_NAME]
        logger.info(f"Returning PersistentMongoClient. Host: {self._client.host}")
        return self._client

    @property
    def db(self):
        logger.info("Getting PersistentMongoClient.db")
        if not self._db:
            logger.info("Generating PersistentMongoClient.db")
            self._db = self.client[db_config.DATABASE_NAME]
        logger.info(f"Returning PersistentMongoClient.db. Host: {self._db.host}")
        return self._db

    async def connect(self) -> None:
        try:
            if not self._is_connected:
                logger.info("Connecting to MongoDB")
                await self.client.server_info()
                self._is_connected = True
                logger.info("Connected to MongoDB")
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self) -> None:
        try:
            if self._is_connected and self._client is not None:
                logger.info("Closing MongoDB connection")
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
