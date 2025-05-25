from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

T = TypeVar("T")
U = TypeVar("U")


class BaseMapper(Generic[T, U], ABC):
    """Base mapper class for mapping between model and schema objects."""

    @abstractmethod
    def to_schema(self, model: T) -> U:
        """Map from model to schema."""
        pass

    @abstractmethod
    def to_model(self, schema: U) -> T:
        """Map from schema to model."""
        pass

    def to_schema_list(self, models: List[T]) -> List[U]:
        """Map a list of models to schemas."""
        return [self.to_schema(model) for model in models]

    def to_model_list(self, schemas: List[U]) -> List[T]:
        """Map a list of schemas to models."""
        return [self.to_model(schema) for schema in schemas]
