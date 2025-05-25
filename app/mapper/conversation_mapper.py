# ChatCompletion to ConversationItem

from app.mapper.base_mapper import BaseMapper
from app.model.chat_model import ChatCompletion
from app.schema.conversation_schema import ConversationItemResponse


class ConversationMapper(BaseMapper[ChatCompletion, ConversationItemResponse]):
    """Mapper for converting between ChatCompletion model and ConversationItem schema."""

    def to_schema(self, model: ChatCompletion) -> ConversationItemResponse:
        """Convert ChatCompletion model to ConversationItem schema."""

        # Get the first message content as title if title is not set
        title = model.title
        if not title and model.messages:
            first_message = model.messages[0]
            title = first_message.content[:20] + "..." if len(first_message.content) > 20 else first_message.content

        return ConversationItemResponse(
            completion_id=model.completion_id,
            title=title,
            create_time=model.created_date,
            update_time=model.last_updated_date,
            is_archived=model.is_archived,
            is_starred=model.is_starred,
        )

    def to_model(self, schema: ConversationItemResponse) -> ChatCompletion:
        raise NotImplementedError("ConversationMapper.to_model is not implemented")
