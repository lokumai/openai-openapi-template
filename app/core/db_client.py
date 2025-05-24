from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock

class DatabaseClient(ABC):
    """Abstract base class for database clients"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def get_database(self) -> Any:
        """Get database instance"""
        pass

class MongoClient(DatabaseClient):
    """Real MongoDB client implementation"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._client: Optional[AsyncIOMotorClient] = None
    
    async def connect(self) -> None:
        self._client = AsyncIOMotorClient(self.connection_string)
    
    async def disconnect(self) -> None:
        if self._client:
            self._client.close()
    
    async def get_database(self) -> AsyncIOMotorClient:
        if not self._client:
            await self.connect()
        return self._client

class MockMongoClient(DatabaseClient):
    """Mock MongoDB client for testing"""
    
    def __init__(self):
        self._client = AsyncMock()
    
    async def connect(self) -> None:
        pass
    
    async def disconnect(self) -> None:
        pass
    
    async def get_database(self) -> AsyncMock:
        return self._client

class DatabaseClientFactory:
    """Factory for creating database clients"""
    
    _instance: Optional['DatabaseClientFactory'] = None
    _client: Optional[DatabaseClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def create_client(cls, db_type: str, connection_string: Optional[str] = None) -> DatabaseClient:
        """
        Create a database client based on the database type
        
        Args:
            db_type: Type of database ('mongodb' or 'mock')
            connection_string: Connection string for the database
            
        Returns:
            DatabaseClient: Instance of the appropriate database client
        """
        if cls._client is None:
            if db_type.lower() == 'mongodb':
                if not connection_string:
                    raise ValueError("Connection string is required for MongoDB")
                cls._client = MongoClient(connection_string)
            elif db_type.lower() == 'mock':
                cls._client = MockMongoClient()
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        
        return cls._client
    
    @classmethod
    async def get_client(cls) -> DatabaseClient:
        """
        Get the current database client instance
        
        Returns:
            DatabaseClient: Current database client instance
        """
        if cls._client is None:
            raise RuntimeError("Database client not initialized")
        return cls._client
    
    @classmethod
    async def reset_client(cls) -> None:
        """Reset the current database client instance"""
        if cls._client:
            await cls._client.disconnect()
        cls._client = None 