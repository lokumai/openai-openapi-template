from functools import wraps
from warnings import deprecated
from fastapi import HTTPException, Request, status
from loguru import logger
import os
import json
from typing import Dict
from environs import Env

env = Env()
env.read_env()

USE_MOCK = env.bool("USE_MOCK", False)
MOCK_DIR = env.str("MOCK_DIR", "resources/mock")

# Deprecated code. because we are using mongomock-motor for database_type=embedded


@deprecated("This function is deprecated. Use database_type=embedded with mongomock-motor instead.")
def get_mock_response(url_path: str, python_module_name: str, python_method_name: str) -> Dict:
    """Get mock response from JSON file."""
    logger.trace(f"BEGIN: url_path: {url_path} python_module_name: {python_module_name} python_method_name: {python_method_name}")
    file_path = None
    try:
        filename = python_module_name + "_" + python_method_name
        filename = filename.replace(".", "_")
        filename = filename.replace("__", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(":", "_")
        filename = filename.replace(" ", "_")
        filename = filename.replace("-", "_")
        filename = filename.replace("app_api_", "")
        logger.trace(f"FileName : {filename}")
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
    """Decorator to handle API request and response"""

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
