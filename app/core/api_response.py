from functools import wraps
import re
from fastapi import HTTPException, Request, status
from loguru import logger
import os
import json
from typing import Dict
from environs import Env

env = Env()
env.read_env()

USE_MOCK = env.bool("USE_MOCK", True)
MOCK_DIR = env.str("MOCK_DIR", "resources/mock")

# Deprecated code. because we are using mongomock-motor for database_type=embedded
# TODO: remove this code after we switch to real database

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

    logger.trace(f"replaced path: {path}")

    # Convert to filename format
    filename = path.replace("/", "_")
    logger.trace(f"filename: {filename}")

    # convert conversations_1 to conversations with dynamic id
    final_filename = re.sub(r"[_][^/]+$", "_id", filename)
    logger.trace(f"final_filename: {final_filename}")

    # Add method suffix
    result = f"{final_filename}_{method}"
    logger.trace(f"END: result: {result}")
    return result


def get_mock_response(url_path: str, python_module_name: str, python_method_name: str) -> Dict:
    """Get mock response from JSON file."""
    logger.trace(f"BEGIN: url_path: {url_path} python_module_name: {python_module_name} python_method_name: {python_method_name}")
    filename = None
    file_path = None
    try:
        # Convert to filename
        # filename = url_to_filename(url_path, method)
        filename = python_module_name + "_" + python_method_name
        filename = filename.replace(".", "_")
        filename = filename.replace("__", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(":", "_")
        filename = filename.replace(" ", "_")
        filename = filename.replace("-", "_")
        filename = filename.replace("app_api_", "")

        # Load mock response
        file_path = os.path.join(MOCK_DIR, f"{filename}.json")

        logger.warning(f"Mock file path: {file_path}")
        with open(file_path, "r") as f:
            result = json.load(f)
            logger.trace(f"END: result: {result}")
            return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{file_path} mock file not found for endpoint: {url_path} [{python_module_name} {python_method_name}]",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{file_path} error loading mock response: {str(e)}",
        )


def api_response():
    """Decorator to handle mock/real API responses."""

    def decorator(func):
        logger.trace(f"BEGIN: decorator: {func}")

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            logger.trace(f"BEGIN: wrapper: {request}")
            logger.trace(f"func: {func.__name__}")
            logger.trace(f"args: {args}")
            logger.trace(f"kwargs: {kwargs}")
            if not request:
                logger.error("Request object not found in args or kwargs")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found",
                )

            logger.trace(f"USE_MOCK value: {USE_MOCK}")
            logger.trace(f"Request path: {request.url.path}")
            logger.trace(f"Request method: {request.method}")

            if USE_MOCK:
                python_method_name = func.__name__
                python_module_name = func.__module__
                logger.warning(f"Using mock response for {request.url.path} [{request.method}] > {python_module_name}.{python_method_name}")
                try:
                    result = get_mock_response(
                        request.url.path,
                        python_module_name,
                        python_method_name,
                    )
                    logger.trace(f"Mock response: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Error getting mock response: {str(e)}")
                    raise
            else:
                logger.warning("Using real response")
                try:
                    result = await func(*args, **kwargs)
                    logger.trace(f"Real response: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Error getting real response: {str(e)}")
                    raise

        return wrapper

    return decorator
