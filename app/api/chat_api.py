# chat api

from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.schema.chat_schema import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    MessageResponse,
    PlotResponse,
)
from app.schema.conversation_schema import (
    ConversationResponse,
    ConversationItemResponse,
)
from app.service.chat_service import ChatService
from app.security.auth_service import AuthService
from app.core.api_response import api_response
from loguru import logger

router = APIRouter(prefix="/v1", tags=["chat"])
service = ChatService()
auth_service = AuthService()


class VersionResponse(BaseModel):
    version: str = "0.0.1"


# version api from pyproject.toml
@router.get("/version", response_model=VersionResponse)
async def get_version():
    return VersionResponse()


################
# chat completion api list
################
# create a chat completion
@router.post("/chat/completions", response_model=ChatCompletionResponse)
@api_response()
async def create_chat_completion(
    chat_completion: ChatCompletionRequest,
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Chat completion API - Given a list of messages comprising a conversation, the model will return a response.
    If completion_id is not provided, start a new chat completion by providing a list of messages.
    If completion_id is provided, the model will continue the conversation from the last message.
    Summary: question -> Send button from chat interface(UI)
    """
    try:
        return await service.handle_chat_completion(chat_completion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get all chat completions
@router.get("/chat/completions", response_model=List[ChatCompletionResponse], deprecated=True)
async def list_chat_completions(
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get all chat completions
    Summary: First load the chat interface(UI) for list of chat completions on the left side.
    """
    logger.debug(f"BEGIN API: list_chat_completions for username: {username}")
    page: int = 1
    limit: int = 10
    sort: dict = {"created_date": -1}
    project: dict = None

    try:
        query = {"created_by": username}
        return await service.find(query, page, limit, sort, project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get a chat completion by id
@router.get("/chat/completions/{completion_id}", response_model=ChatCompletionResponse)
@api_response()
async def retrieve_chat_completion(
    completion_id: str,
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get a chat completion by id
    Summary: Click on a chat completion on the left side to load the chat completion on the right side.
    """
    try:
        return await service.find_by_id(completion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get all messages for a chat completion
@router.get("/chat/completions/{completion_id}/messages", response_model=List[MessageResponse], deprecated=True)
@api_response()
async def list_messages(
    completion_id: str,
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get all messages for a chat completion
    Summary: Click on a chat completion on the left side to load the chat completion on the right side.
    """
    try:
        return await service.find_messages(completion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


################
# plot api list
################
# get a plot for a message
@router.get("/chat/completions/{completion_id}/messages/{message_id}/plot", response_model=PlotResponse)
@api_response()
async def retrieve_plot(
    completion_id: str,
    message_id: str,
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get a plot figure for a message to visualize the data
    Summary: Click on a message on the right side to load the plot on the right side.
    """
    try:
        return await service.find_plot(completion_id, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


################
# conversation api list
################
# GET https://chatgpt.com/backend-api/conversations
# GET https://chatgpt.com/backend-api/conversations/{completion_id}


# get all conversations
@router.get("/conversations", response_model=ConversationResponse, response_model_exclude_none=True)
async def list_conversations(
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get all conversations
    """
    logger.debug(f"Listing conversations for username: {username}")
    try:
        return await service.find_all_conversations(username)
    except Exception as e:
        logger.error(f"Error in list_conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# get a conversation by id


@router.get("/conversations/{completion_id}", response_model=ConversationItemResponse, response_model_exclude_none=True)
async def retrieve_conversation(
    completion_id: str,
    request: Request,
    username: str = Depends(auth_service.verify_credentials),
):
    """
    Get a conversation by id
    """
    logger.debug(f"Retrieving conversation with completion_id: {completion_id}")
    try:
        return await service.find_conversation_by_id(completion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
