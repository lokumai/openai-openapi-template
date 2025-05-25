from fastapi import APIRouter
from fastapi import Request, Depends, HTTPException
from loguru import logger

from app.schema.conversation_schema import ConversationResponse, ConversationItemResponse
from app.service.chat_service import ChatService
from app.security.auth_service import AuthService


router = APIRouter(prefix="/v1", tags=["conversation"])
chat_service = ChatService()
auth_service = AuthService()


################
# conversation api
# It means User chat history
################
# GET https://chatgpt.com/platform-api/conversations
# GET https://chatgpt.com/platform-api/conversations/{completion_id}


# get all conversations for current user
@router.get("/conversations", response_model=ConversationResponse, response_model_exclude_none=True)
async def list_conversations(username: str = Depends(auth_service.verify_credentials)) -> ConversationResponse:
    """
    Get all conversations by current user
    """
    logger.debug(f"Listing conversations for username: {username}")
    try:
        return await chat_service.find_all_conversations(username)
    except Exception as e:
        logger.error(f"Error in list_conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# get a conversation by id for current user
@router.get("/conversations/{completion_id}", response_model=ConversationItemResponse, response_model_exclude_none=True)
async def retrieve_conversation(
    completion_id: str, request: Request, username: str = Depends(auth_service.verify_credentials)
) -> ConversationItemResponse:
    """
    Get a conversation by id for current user
    """
    logger.debug(f"Retrieving conversation with completion_id: {completion_id}")
    try:
        return await chat_service.find_conversation_by_id(completion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
