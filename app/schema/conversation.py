from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ConversationItemResponse(BaseModel):
    """Represents an individual conversation record in the platform's chat history."""

    completion_id: str = Field(description="Unique identifier for the conversation in UUID format.")
    title: str = Field(description="Title or name of the conversation, describing its content or purpose.")
    create_time: datetime = Field(
        description="Timestamp when the conversation was created, in ISO 8601 format (e.g., '2025-05-22T10:54:37.569747Z')."
    )
    update_time: datetime = Field(description="Timestamp when the conversation was last updated, in ISO 8601 format.")
    mapping: Optional[dict] = Field(
        default=None,
        description="Optional dictionary containing additional conversation metadata or mappings, if applicable.",
    )
    current_node: Optional[str] = Field(
        default=None,
        description="Identifier for the current node or state in the conversation flow, if used.",
    )
    conversation_template_id: Optional[str] = Field(
        default=None,
        description="Identifier for the conversation template used, if any.",
    )
    gizmo_id: Optional[str] = Field(
        default=None,
        description="Identifier for the gizmo or tool associated with the conversation, if applicable.",
    )
    is_archived: bool = Field(description="Indicates whether the conversation is archived.")
    is_starred: Optional[bool] = Field(
        default=None,
        description="Indicates whether the conversation is marked as starred or favorite, if set.",
    )
    is_do_not_remember: Optional[bool] = Field(
        default=None,
        description="Indicates whether the conversation is excluded from memory or history, if set.",
    )
    memory_scope: str = Field(description="Scope of the conversation's memory, e.g., 'global_enabled' for global memory access.")
    workspace_id: Optional[str] = Field(
        default=None,
        description="Identifier for the workspace the conversation belongs to, if applicable.",
    )
    async_status: Optional[str] = Field(
        default=None,
        description="Status of any asynchronous operations related to the conversation, if applicable.",
    )
    safe_urls: List[str] = Field(description="List of URLs deemed safe for the conversation context.")
    blocked_urls: List[str] = Field(description="List of URLs blocked for the conversation context.")
    conversation_origin: Optional[str] = Field(
        default=None,
        description="Origin or source of the conversation, if specified.",
    )
    snippet: Optional[str] = Field(
        default=None,
        description="Optional brief excerpt or summary of the conversation content.",
    )


class ConversationResponse(BaseModel):
    """Represents the response object containing a list of conversation records and pagination metadata from the platform."""

    items: List[ConversationItemResponse] = Field(description="List of conversation items representing the user's chat history.")
    total: int = Field(description="Total number of conversations available in the user's history.")
    limit: int = Field(description="Maximum number of conversation items returned in this response.")
    offset: int = Field(description="Starting index of the conversation items in this response, used for pagination.")
