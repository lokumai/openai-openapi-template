# mongodb client with motor and pymongo

from abc import ABC, abstractmethod
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
from app.config.db import db_config
from loguru import logger
from typing import Optional
from environs import Env

env = Env()
env.read_env()

DB_DATABASE_TYPE = env.str("DB_DATABASE_TYPE", "mongodb")


class DatabaseClient(ABC):
    """Abstract base class for database clients"""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection"""
        pass

    @property
    @abstractmethod
    def client(self):
        """Get the database client"""
        pass

    @property
    @abstractmethod
    def db(self):
        """Get the database instance"""
        pass


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


class EmbeddedMongoClient(DatabaseClient):
    """Mock MongoDB client implementation for testing"""

    def __init__(self):
        logger.info("Initializing EmbeddedMongoClient")
        self._client: Optional[AsyncMongoMockClient] = None
        self._db = None
        self._is_connected: bool = False
        logger.info("EmbeddedMongoClient initialized")

    @property
    def client(self) -> AsyncMongoMockClient:
        logger.info("Getting EmbeddedMongoClient")
        if not self._client:
            logger.info("Generating EmbeddedMongoClient")
            self._client = AsyncMongoMockClient()
            self._db = self._client[db_config.DATABASE_NAME]
        logger.info(f"Returning EmbeddedMongoClient. Host: {self._client.host}")
        return self._client

    @property
    def db(self):
        logger.info("Getting EmbeddedMongoClient.db")
        if not self._db:
            logger.info("Generating EmbeddedMongoClient.db")
            self._db = self.client[db_config.DATABASE_NAME]
        logger.info(f"Returning EmbeddedMongoClient.db. Host: {self._db.host}")
        return self._db

    async def connect(self) -> None:
        try:
            if not self._is_connected:
                logger.info("Connecting to EmbeddedMongoClient")
                self._is_connected = True
                logger.info("Connected to EmbeddedMongoClient")
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to EmbeddedMongoClient: {e}")
            raise

    async def close(self) -> None:
        try:
            if self._is_connected and self._client is not None:
                logger.info("Closing EmbeddedMongoClient connection")
                self._client = None
                self._db = None
                self._is_connected = False
                logger.info("Disconnected from EmbeddedMongoClient")
        except Exception as e:
            logger.warning(f"Error while closing EmbeddedMongoClient connection: {e}")
            self._client = None
            self._db = None
            self._is_connected = False


class DatabaseClientFactory:
    """Factory class for creating database clients"""

    _instance: Optional["DatabaseClientFactory"] = None
    _client: Optional[DatabaseClient] = None

    def __new__(cls):
        logger.info("Creating DatabaseClientFactory")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("DatabaseClientFactory created")
        logger.info(f"Returning DatabaseClientFactory. Host: {cls._instance.client.host}")
        return cls._instance

    @classmethod
    def get_client(cls) -> DatabaseClient:
        """Get the appropriate database client based on configuration"""
        logger.info(f"Getting DatabaseClientFactory.client with DB_DATABASE_TYPE: {DB_DATABASE_TYPE}")
        logger.info(f"mongodb uri: {db_config.get_mongo_uri()}")
        if cls._client is None:
            if DB_DATABASE_TYPE == "mongodb":
                logger.info("Creating PersistentMongoClient")
                cls._client = PersistentMongoClient()
            else:
                logger.info("Creating EmbeddedMongoClient")
                cls._client = EmbeddedMongoClient()
        logger.info(f"Returning DatabaseClientFactory.client. Host: {cls._client.client.host}")
        return cls._client


# Global instance
db_client = DatabaseClientFactory.get_client()
