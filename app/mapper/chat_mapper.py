from app.mapper.base_mapper import BaseMapper
from app.model.chat_model import ChatCompletion, ChatMessageModel
from app.schema.chat_schema import ChatCompletionResponse, ChatCompletionRequest, ChatMessageResponse, ChoiceResponse


class ChatMapper(BaseMapper[ChatCompletion, ChatCompletionResponse]):
    """Mapper for converting between ChatCompletion model and schema objects."""

    def to_schema(self, model: ChatCompletion) -> ChatCompletionResponse:
        """Convert ChatCompletion model to ChatCompletionResponse schema."""
        # Convert datetime to Unix timestamp
        created_timestamp = int(model.created_date.timestamp()) if model.created_date else None

        # Map the last message to a response message
        last_message = model.messages[-1] if model.messages else None
        message_response = None
        if last_message:
            message_response = ChatMessageResponse(
                message_id=last_message.message_id,
                role=last_message.role,
                content=last_message.content,
                figure=last_message.figure,
                created_date=last_message.created_date,
            )

        # Create choice response
        choice = ChoiceResponse(index=0, message=message_response, finish_reason="stop") if message_response else None

        return ChatCompletionResponse(
            completion_id=model.completion_id, model=model.model, created=created_timestamp, choices=[choice] if choice else []
        )

    def to_model(self, schema: ChatCompletionRequest) -> ChatCompletion:
        """Convert ChatCompletionRequest schema to ChatCompletion model."""
        # Convert messages to ChatMessage objects
        messages = []
        if schema.messages:
            for msg in schema.messages:
                messages.append(ChatMessageModel(role=msg.role, content=msg.content, figure=None, message_id=None))

        return ChatCompletion(
            title=schema.title,
            completion_id=schema.completion_id,
            model=schema.model,
            messages=messages,
            stream=schema.stream,
            created_by=schema.created_by,
            created_date=schema.created_date,
            object_field=schema.object_field,
            is_archived=schema.archived,
            is_starred=schema.starred,
            last_updated_by=schema.last_updated_by,
            last_updated_date=schema.last_updated_date,
        )
