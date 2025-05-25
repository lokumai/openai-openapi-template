# ChatCompletion to ConversationItem

from app.mapper.base_mapper import BaseMapper
from app.model.chat_model import ChatCompletion
from app.schema.conversation_schema import ConversationItemResponse


class ConversationMapper(BaseMapper[ChatCompletion, ConversationItemResponse]):
    """Mapper for converting between ChatCompletion model and ConversationItem schema."""

    def to_schema(self, model: ChatCompletion) -> ConversationItemResponse:
        """Convert ChatCompletion model to ConversationItem schema."""
        # Convert datetime to Unix timestamp
        created_timestamp = int(model.created_date.timestamp()) if model.created_date else None
        last_updated_timestamp = int(model.last_updated_date.timestamp()) if model.last_updated_date else None

        # Get the first message content as title if title is not set
        title = model.title
        if not title and model.messages:
            first_message = model.messages[0]
            title = first_message.content[:20] + "..." if len(first_message.content) > 20 else first_message.content

        return ConversationItemResponse(
            completion_id=model.completion_id,
            title=title,
            create_time=created_timestamp,
            update_time=last_updated_timestamp,
            is_archived=model.is_archived,
            is_starred=model.is_starred,
        )

    def to_model(self, schema: ConversationItemResponse) -> ChatCompletion:
        raise NotImplementedError("ConversationMapper.to_model is not implemented")
