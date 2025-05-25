from pydantic import BaseModel


class UserChatAgentRequest(BaseModel):
    message: str


class AssistantChatAgentResponse(BaseModel):
    message: str
    figure: dict | None = None
