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
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            url_path = request.url.path
            method = request.method
            logger.debug(f"BEGIN: url_path: {url_path} method: {method}")
            if USE_MOCK:
                logger.warning("Using mock response")
                result = get_mock_response(url_path, method)
                logger.trace(f"END: result: {result}")
                return result
            else:
                # Call original function for real response
                result = await func(request, *args, **kwargs)
                logger.trace(f"END: result: {result}")
                return result
        return wrapper
    return decorator