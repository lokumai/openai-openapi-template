import json
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat_api
from app.config.log import log_config
from loguru import logger
from environs import Env
from contextlib import asynccontextmanager
from app.db.factory import db_client
from gradio_chatbot import build_gradio_app, app_auth
import gradio as gr
import os
from app.core.initial_setup.setup import InitialSetup

print(log_config.get_log_level())

env = Env()
env.read_env()

DB_DATABASE_TYPE = env.str("DB_DATABASE_TYPE", "mongodb")

# Hugging Face Spaces için özel yapılandırma
IS_HF_SPACE = os.environ.get("SPACE_ID") is not None
SPACE_URL = "https://lokumai-openai-openapi-template.hf.space" if IS_HF_SPACE else "http://localhost:7860"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    await db_client.connect()

    # Run initial setup if database type is embedded
    initial_setup = InitialSetup()
    await initial_setup.setup()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await db_client.close()


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
    {
        "name": "chat",
        "description": "Chat API : Given a list of messages comprising a conversation, the model will return a response.",
    }
]

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    debug=True,
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
app.include_router(chat_api.router)

# Build and mount Gradio app
demo = build_gradio_app()
app = gr.mount_gradio_app(app, demo, path="/ui", auth=app_auth)


@app.get("/")
async def root():
    """Redirect root to Gradio UI"""
    return RedirectResponse(url="/ui")


@app.get("/manifest.json")
async def get_manifest():
    """Return the web app manifest"""
    manifest_path = os.path.join(os.path.dirname(__file__), "static", "manifest.json")
    with open(manifest_path, "r") as f:
        return JSONResponse(json.load(f))


# uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload
