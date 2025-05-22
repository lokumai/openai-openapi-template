from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.api import chat_api
from app.config.log import log_config
from loguru import logger
from environs import Env
from contextlib import asynccontextmanager
from app.db.client import mongodb

print(log_config.get_log_level())

env = Env()
env.read_env()
 
STORAGE_TYPE = env.str("STORAGE_TYPE", "mongodb")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    if STORAGE_TYPE == "mongodb":
        await mongodb.connect()
    yield

    # Shutdown
    logger.info("Shutting down application...")
    if STORAGE_TYPE == "mongodb":
        await mongodb.close()


VERSION = "0.3.0"
TITLE = "Talk to your data chat and visualize API"
DESCRIPTION = """
Talk to your data chat and visualize API

    ## Chat
    You can use the chat API to talk to your data and visualize the results.

    ## Authentication
    All endpoints require API key authentication using the `Authorization` header.
    API keys are in the format: `sk-{username}-{base64_encoded_data}`
    
    ## Endpoints
    ### Chat (openai compatible APIs) - Given a list of messages comprising a conversation, the model will return a response.
    - GET  `/v1/chat/completions`: listChatCompletions - List stored chat completions. Only Chat completions that have been stored with the `store` parameter set to `true` will be returned.
    - POST `/v1/chat/completions`: createChatCompletion - Create a new chat completion.
    - GET  `/v1/chat/completions/{completion_id}`: getChatCompletion - Get a stored chat completion. Only Chat Completions that have been created with the `store` parameter set to `true` will be returned.
    - POST `/v1/chat/completions/{completion_id}`: modifyChatCompletion - Modify a stored chat completion.
    - DELETE `/v1/chat/completions/{completion_id}`: deleteChatCompletion - Delete a stored chat completion.
    - GET  `/v1/chat/completions/{completion_id}/messages`: getChatCompletionMessages - Get the messages in a stored chat completion.

    ### Plots( custom endpoints)
    - GET  `/v1/chat/completions/{completion_id}/messages/{message_id}/plots`: getChatPlotByMessage - Get the plot for a specific message in a chat.
  
"""

openapi_tags = [
    {"name": "chat", "description": "Chat API : Given a list of messages comprising a conversation, the model will return a response."}
]

app = FastAPI(
    title= TITLE,
    description= DESCRIPTION,
    version= VERSION,
    docs_url= "/docs",
    redoc_url= "/redoc",
    openapi_url= "/openapi.json",
    lifespan= lifespan,
    openapi_tags= openapi_tags,
    debug= True,
)

# Configure OpenAPI security scheme
app.openapi_components = {
    "securitySchemes": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "API key in the format: sk-{username}-{base64_encoded_data}",
        }
    }
}

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
app.include_router(chat_api.router)

@app.get("/")
async def root():
    return RedirectResponse(url="http://localhost:7861")

# uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload
