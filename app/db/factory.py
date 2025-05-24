from typing import Optional
from loguru import logger
from app.db.client import DatabaseClient
from app.db.mongo import PersistentMongoClient
from app.db.embedded import EmbeddedMongoClient
from app.config.db import db_config


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
    def get_client(cls, force_new: bool = False) -> DatabaseClient:
        """Get the appropriate database client based on configuration"""
        logger.info(f"Getting DatabaseClientFactory.client with DB_DATABASE_TYPE: {db_config.DATABASE_TYPE}")

        if force_new or cls._client is None:
            if db_config.DATABASE_TYPE == "mongodb":
                logger.info("Creating PersistentMongoClient")
                cls._client = PersistentMongoClient()
            else:
                logger.info("Creating EmbeddedMongoClient")
                cls._client = EmbeddedMongoClient()
        logger.info(f"Returning DatabaseClientFactory.client. Host: {cls._client.client.host}")
        return cls._client


# Global instance
db_client = DatabaseClientFactory.get_client()
