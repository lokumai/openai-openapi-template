# chat api

from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from app.schema.chat_schema import ChatCompletionRequest, ChatCompletionResponse, ChatMessageResponse
from app.service.chat_service import ChatService
from app.security.auth_service import AuthService
from loguru import logger

router = APIRouter(prefix="/v1", tags=["chat"])
service = ChatService()
auth_service = AuthService()


################
# chat completion api list
################
# create a chat completion
@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    chat_completion: ChatCompletionRequest, request: Request, username: str = Depends(auth_service.verify_credentials)
):
    """
    Chat completion API - Given a list of messages comprising a conversation, the model will return a response.
    If completion_id is not provided, start a new chat completion by providing a list of messages.
    If completion_id is provided, the model will continue the conversation from the last message.
    Summary: question -> Send button from chat interface(UI)
    """
    logger.debug(f"BEGIN API: Create Chat Completion for username: {username}")
    try:
        result = await service.handle_chat_completion(chat_completion, username)
        logger.debug("END API: Create Chat Completion")
        return result
    except Exception as e:
        logger.error(f"Error in create_chat_completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# get all chat completions
@router.get("/chat/completions", response_model=List[ChatCompletionResponse], deprecated=True)
async def list_chat_completions(request: Request, username: str = Depends(auth_service.verify_credentials)):
    """
    Get all chat completions
    Summary: First load the chat interface(UI) for list of chat completions on the left side.
    """
    logger.debug(f"BEGIN API: list_chat_completions for username: {username}")
    page: int = 1
    limit: int = 10
    sort: dict = {"created_date": -1}
    project: dict = {}

    try:
        query = {"created_by": username}
        return await service.find(query, page, limit, sort, project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get a chat completion by id
@router.get("/chat/completions/{completion_id}", response_model=ChatCompletionResponse)
async def retrieve_chat_completion(completion_id: str, request: Request, username: str = Depends(auth_service.verify_credentials)):
    """
    Get a chat completion by id
    Summary: Click on a chat completion on the left side to load the chat completion on the right side.
    """
    try:
        return await service.find_by_id(completion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get all messages for a chat completion
@router.get("/chat/completions/{completion_id}/messages", response_model=List[ChatMessageResponse], deprecated=True)
async def list_messages(completion_id: str, request: Request, username: str = Depends(auth_service.verify_credentials)):
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
@router.get(
    "/chat/completions/{completion_id}/messages/{message_id}/plot",
    response_model=Optional[dict[str, Any]],
    response_model_exclude_none=True,
)
async def retrieve_plot(completion_id: str, message_id: str, request: Request, username: str = Depends(auth_service.verify_credentials)):
    """
    Get a plot figure for a message to visualize the data
    Summary: Click on a message on the right side to load the plot on the right side.
    """
    try:
        return await service.find_plot_by_message(completion_id, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
