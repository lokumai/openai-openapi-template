# mongodb client with motor and pymongo

from abc import ABC, abstractmethod
from typing import  Protocol

class DatabaseClientProtocol(Protocol):
    """
    Python duck-typing protocol for database clients that implements the following methods:
    - connect
    - close
    - client
    - db

    This protocol is used to ensure that the database client implements the required methods and properties.

    References:
    - https://en.wikipedia.org/wiki/Duck_typing
    - https://docs.python.org/3/library/typing.html#typing.Protocol
    - https://www.python.org/dev/peps/pep-0544/
    - https://realpython.com/duck-typing-python/
    """
    async def connect(self) -> None: ...
    async def close(self) -> None: ...
    @property
    def client(self): ...
    @property
    def db(self): ...


class DatabaseClient(ABC, DatabaseClientProtocol):
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
