from typing import Optional
from mongomock_motor import AsyncMongoMockClient
from app.config.db import db_config
from loguru import logger
from app.db.client import DatabaseClient


class EmbeddedMongoClient(DatabaseClient):
    """
    Mock MongoDB client implementation for local machine and development environment.
    This client is used to connect to a mock MongoDB instance that is running in the local machine.
    It is used to test/dev/local the application without the need to have a real MongoDB instance running.
    """

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
