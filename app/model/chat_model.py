# chat model for chat completion database

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any


class ChatMessageModel(BaseModel):
    """
    A message in a chat completion.
    """

    message_id: Optional[str] = Field(None, description="The unique identifier for the message")
    role: str = Field(..., description="The role of the message sender", examples=["user", "assistant", "system"])
    content: str = Field(..., description="The content of the message")
    figure: Optional[dict[str, Any]] = Field(None, description="The figure data for visualization")
    created_date: Optional[datetime] = Field(None, description="The timestamp of the message")

    def __str__(self):
        return f"""
        ChatMessage(
            message_id={self.message_id},
            role={self.role},
            content={self.content},
            figure={self.figure},
            created_date={self.created_date})
            """

    def __repr__(self):
        return self.__str__()

    def __format__(self, format_spec):
        return self.__str__()


class ChatCompletion(BaseModel):
    """
    A chat completion.
    """

    id: Optional[ObjectId] = Field(alias="_id", default_factory=ObjectId, description="MongoDB unique identifier")
    completion_id: Optional[str] = Field(None, description="The unique identifier for the chat completion")

    # openai compatible fields
    model: Optional[str] = Field(None, description="The model used for the chat completion", examples=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    messages: Optional[List[ChatMessageModel]] = Field(None, description="The messages in the chat completion")

    # not implemented yet
    # temperature: float = Field(default=0.7,ge=0.0, le=1.0, description="What sampling temperature to use, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.")
    # max_tokens: int = Field(default=1000, ge=0, le=10000, description="The maximum number of tokens to generate in the chat completion.")
    # top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.")
    # frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.")
    # presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.")
    # n: int = Field(default=1, ge=1, le=10, description="How many chat completion choices to generate for each prompt.")

    stream: bool = Field(
        False,
        description="If set to true, the model response data will be streamed to the client as it is generated using server-sent events.",
    )

    title: Optional[str] = Field(None, description="The title of the chat completion")
    object_field: str = Field("chat.completion", alias="object_field", description="The object field of the chat completion")
    is_archived: bool = Field(False, description="Whether the chat completion is archived")
    is_starred: bool = Field(False, description="Whether the chat completion is starred")

    # audit fields
    created_by: Optional[str] = Field(None, description="The user who created the chat completion")
    created_date: Optional[datetime] = Field(None, description="The date and time the chat completion was created")
    last_updated_by: Optional[str] = Field(None, description="The user who last updated the chat completion")
    last_updated_date: Optional[datetime] = Field(None, description="The date and time the chat completion was last updated")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda o: str(o), datetime: lambda o: o.isoformat()}

    def __str__(self):
        return f"""
        ChatCompletion( 
            completion_id={self.completion_id},
            model={self.model},
            messages={self.messages},
            created_by={self.created_by},
            created_date={self.created_date},
            last_updated_by={self.last_updated_by},
            last_updated_date={self.last_updated_date})
            """

    def __repr__(self):
        return self.__str__()

    def __format__(self, format_spec):
        return self.__str__()
