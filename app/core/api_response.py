from functools import wraps
from fastapi import HTTPException, Request, status
from loguru import logger
import os
import json
from typing import Dict
from environs import Env

env = Env()
env.read_env()

USE_MOCK = env.bool("USE_MOCK", True)


def url_to_filename(url: str, method: str) -> str:
    """
    Convert API URL to mock filename.
    Example: 
    - Input: GET "/v1/chat/completions" -> "chat_completions_GET.json"
    - Input: GET "/v1/chat/completions/{completion_id}" -> "chat_completions_id_GET.json"
    - Input: GET "/v1/chat/completions/123/messages" -> "chat_completions_id_messages_GET.json"
    """
    logger.trace(f"BEGIN: url: {url} method: {method}")
    # Remove version prefix and leading/trailing slashes
    path = url.strip("/")
    if path.startswith("v1/"):
        path = path[3:]
    
    # Replace path parameters with descriptive names
    path = path.replace("{completion_id}", "id")
    path = path.replace("{message_id}", "id")
    
    # Convert to filename format
    filename = path.replace("/", "_")
    
    # Add method suffix
    result = f"{filename}_{method}"
    logger.trace(f"END: result: {result}")
    return result


def get_mock_response(url_path: str, method: str) -> Dict:
    """Get mock response from JSON file."""
    logger.trace(f"BEGIN: url_path: {url_path} method: {method}")
    filename = None
    try:
        # Convert to filename
        filename = url_to_filename(url_path, method)
        
        # Load mock response
        file_path = os.path.join(os.path.dirname(__file__), "mock", f"{filename}.json")
        with open(file_path, "r") as f:
            result = json.load(f)
            logger.trace(f"END: result: {result}")
            return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{filename} mock file not found for endpoint: {url_path} [{method}]"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{filename} error loading mock response: {str(e)}"
        )


def api_response():
    """Decorator to handle mock/real API responses."""
    def decorator(func):
        logger.debug(f"BEGIN: decorator: {func}")
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            logger.debug(f"BEGIN: wrapper: {request}")
            if not request:
                logger.error("Request object not found in args or kwargs")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )

            logger.debug(f"USE_MOCK value: {USE_MOCK}")
            logger.debug(f"Request path: {request.url.path}")
            logger.debug(f"Request method: {request.method}")

            if USE_MOCK:
                logger.warning("Using mock response")
                try:
                    result = get_mock_response(request.url.path, request.method)
                    logger.debug(f"Mock response: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Error getting mock response: {str(e)}")
                    raise
            else:
                logger.warning("Using real response")
                try:
                    result = await func(*args, **kwargs)
                    logger.debug(f"Real response: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Error getting real response: {str(e)}")
                    raise

        return wrapper
    return decorator