import datetime
from app.mapper.base_mapper import BaseMapper
from app.model.chat_model import ChatCompletion, ChatMessageModel
from app.schema.chat_schema import ChatCompletionResponse, ChatCompletionRequest, ChatMessageResponse, ChoiceResponse
from loguru import logger


def to_message_schema(model: ChatMessageModel) -> ChatMessageResponse:
    """Convert ChatMessageModel to ChatMessageResponse schema."""
    return ChatMessageResponse(
        message_id=model.message_id,
        role=model.role,
        content=model.content,
        figure=model.figure,
        created_date=model.created_date,
    )


class ChatMapper(BaseMapper[ChatCompletion, ChatCompletionResponse]):
    """Mapper for converting between ChatCompletion model and schema objects."""

    def to_schema(self, model: ChatCompletion, convert_last_message: bool = False) -> ChatCompletionResponse:
        """Convert ChatCompletion model to ChatCompletionResponse schema."""
        # Convert datetime to Unix timestamp
        created_timestamp = int(model.created_date.timestamp()) if model.created_date else int(datetime.now().timestamp())
        choices = []
        if convert_last_message:
            last_message = model.messages[-1]
            choices.append(ChoiceResponse(index=0, message=to_message_schema(last_message), finish_reason="stop"))
        else:
            index = 0
            for message in model.messages:
                choices.append(ChoiceResponse(index=index, message=to_message_schema(message), finish_reason="stop"))
                index += 1

        return ChatCompletionResponse(completion_id=model.completion_id, model=model.model, created=created_timestamp, choices=choices)

    def to_model(self, schema: ChatCompletionRequest) -> ChatCompletion:
        """Convert ChatCompletionRequest schema to ChatCompletion model."""
        # Convert messages to ChatMessage objects
        messages = []
        if schema.messages:
            for msg in schema.messages:
                messages.append(ChatMessageModel(role=msg.role, content=msg.content, figure=None, message_id=None))
        try:
            return ChatCompletion(completion_id=schema.completion_id, model=schema.model, messages=messages, stream=schema.stream)
        except Exception as e:
            logger.error(f"Error converting ChatCompletionRequest to ChatCompletion: {e}")
            raise
