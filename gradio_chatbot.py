import json
import gradio as gr
import environs
import httpx
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os
from loguru import logger
import plotly.graph_objects as go

# Environment configuration
env = environs.Env()
env.read_env()

# Hugging Face Spaces için özel yapılandırma
IS_HF_SPACE = os.environ.get("SPACE_ID") is not None
SPACE_URL = (
    "https://lokumai-openai-openapi-template.hf.space"
    if IS_HF_SPACE
    else "http://localhost:7860"
)

# API Configuration
BASE_URL = env.str("BASE_URL", SPACE_URL)
API_KEY = env.str("API_KEY", "sk-test-xxx")
CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"

# Get absolute paths for static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")

# Avatar paths
USER_AVATAR = os.path.join(AVATAR_DIR, "user.png")
BOT_AVATAR = os.path.join(AVATAR_DIR, "bot.png")

# Custom CSS for fonts
CUSTOM_CSS = """
@font-face {{
    font-family: 'UI Sans Serif';
    src: url('/static/fonts/ui-sans-serif/ui-sans-serif-Regular.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
}}

@font-face {{
    font-family: 'UI Sans Serif';
    src: url('/static/fonts/ui-sans-serif/ui-sans-serif-Bold.woff2') format('woff2');
    font-weight: bold;
    font-style: normal;
}}

@font-face {{
    font-family: 'System UI';
    src: url('/static/fonts/system-ui/system-ui-Regular.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
}}

@font-face {{
    font-family: 'System UI';
    src: url('/static/fonts/system-ui/system-ui-Bold.woff2') format('woff2');
    font-weight: bold;
    font-style: normal;
}}

.gradio-container {{
    font-family: 'UI Sans Serif', 'System UI', sans-serif;
}}

/* Improve chat interface */
.chat-message {{
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
}}

.chat-message.user {{
    background-color: #f3f4f6;
}}

.chat-message.bot {{
    background-color: #eef2ff;
}}

/* Improve button styles */
button {{
    transition: all 0.2s ease-in-out;
}}

button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

/* Improve input area */
textarea {{
    border-radius: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #e5e7eb;
    transition: border-color 0.2s ease-in-out;
}}

textarea:focus {{
    border-color: #4f46e5;
    outline: none;
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}}
"""


class MessageStatus(Enum):
    """Enum for message status"""

    SUCCESS = "Success"
    ERROR = "Error"


@dataclass
class MessageResponse:
    """Data class for message response"""

    status: MessageStatus
    content: str
    figure: Optional[dict] = None
    error: Optional[str] = None


class ChatAPI:
    """Class to handle chat API interactions"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.endpoint = f"{base_url}/v1/chat/completions"

    async def send_message(self, prompt: str) -> MessageResponse:
        """
        Send a message to the chat API

        Args:
            prompt (str): The message to send

        Returns:
            MessageResponse: The response from the API
        """
        logger.trace(f"Calling chat API with prompt: {prompt}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "model": "gpt-3.5-turbo",
                        "completion_id": "new_chat",
                        "stream": True,
                    },
                    timeout=30.0,  # Add timeout
                )

                if response.status_code != 200:
                    logger.error(f"API Error: {response.text}")
                    return MessageResponse(
                        status=MessageStatus.ERROR,
                        content="",
                        figure=None,
                        error=f"API Error: {response.text}",
                    )

                result = response.json()
                logger.trace("######################## BEGIN API response #########################")
                logger.trace(json.dumps(result, indent=4))
                logger.trace("######################## END API response #########################")
                
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    figure = message.get("figure", None)
                    logger.trace(f"Figure: {figure}")
                    content = message.get("content", "Content not found")
                    logger.trace(f"Last message: {content}")
                    return MessageResponse(
                        status=MessageStatus.SUCCESS, content=content, figure=figure
                    )
                else:
                    logger.error("Invalid API response")
                    return MessageResponse(
                        status=MessageStatus.ERROR,
                        content="",
                        error="Invalid API response",
                    )
                
        except httpx.TimeoutException:
            logger.error("API request timed out")
            return MessageResponse(
                status=MessageStatus.ERROR,
                content="",
                error="Request timed out. Please try again.",
            )
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return MessageResponse(
                status=MessageStatus.ERROR, content="", error=f"Error: {str(e)}"
            )


class ChatInterface:
    """Class to handle the Gradio chat interface"""

    def __init__(self, chat_api: ChatAPI):
        self.chat_api = chat_api
        self.demo = self._build_interface()

    def _build_interface(self) -> gr.Blocks:
        """
        Build the Gradio interface

        Returns:
            gr.Blocks: The Gradio interface
        """
        with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS) as demo:
            # Header
            gr.Markdown("""
            # 🤖 Data Chatbot
            
            This chatbot allows you to chat with your data and visualize it.
            Please enter your question in the text box below and click the "Send" button.
            
            > 📚 API Documentation: [https://lokumai-openai-openapi-template.hf.space/docs](https://lokumai-openai-openapi-template.hf.space/docs)
            """)

            # Main chat interface
            with gr.Row():
                with gr.Column(scale=4):
                    # Chat history display
                    chatbot = gr.Chatbot(
                        label="Chat History",
                        height=400,
                        show_copy_button=True,
                        avatar_images=(USER_AVATAR, BOT_AVATAR),
                        elem_classes=["chat-message"],
                    )

                    # Plotly graph display
                    plot = gr.Plot(label="Data Visualization")

                    # Message input area
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Enter your question here...",
                            lines=3,
                            scale=4,
                            elem_classes=["message-input"],
                        )
                        submit_btn = gr.Button("Send", variant="primary", scale=1)

                    # Control buttons
                    with gr.Row():
                        clear_btn = gr.Button("Clear Chat", variant="secondary")
                        retry_btn = gr.Button("Retry", variant="secondary")

                    # Status and last message display
                    status = gr.Textbox(label="Status", interactive=False)
                    last_message = gr.Textbox(label="Last Message", interactive=False)

            # Event handlers
            async def user_message(
                message: str, history: List[List[str]]
            ) -> Tuple[List[List[str]], str, str, str, object]:
                """Handle user message submission"""
                if not message.strip():
                    return history, "", "Please enter a message.", "", None
                
                logger.debug(f"User message: {message}")

                history.append([message, ""])
                response = await self.chat_api.send_message(message)

                if response.status == MessageStatus.SUCCESS:
                    content = response.content
                    figure_data = response.figure
                    logger.trace(f"Figure data: {figure_data}")
                    figure = None
                    if isinstance(figure_data, dict):
                        logger.trace(f"Plotly input: {figure_data}")
                        try:
                            figure = go.Figure(figure_data)
                            logger.trace(f"Plotly figure: {figure.to_dict()}")
                        except Exception as e:
                            logger.error(f"Error creating plotly figure: {e}")
                            figure = None
                            history[-1][1] += (
                                "\n\n⚠️ Graph data is not valid, cannot be displayed."
                            )
                    history[-1][1] = content
                    return history, "", "Message sent successfully.", content, figure
                else:
                    history[-1][1] = f"❌ {response.error}"
                    return history, "", f"Error: {response.error}", "", None

            def clear_history() -> Tuple[List[List[str]], str, str, str, dict]:
                """Clear chat history"""
                return [], "", "Chat cleared.", "", None

            def retry_last_message(
                history: List[List[str]],
            ) -> Tuple[List[List[str]], str, str, str, dict]:
                """Retry the last message"""
                if not history:
                    return history, "", "No message to retry.", "", None

                last_message = history[-1][0]
                return (
                    history[:-1],
                    last_message,
                    "Last message will be retried.",
                    "",
                    None,
                )

            # Connect event handlers to UI elements
            submit_btn.click(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, status, last_message, plot],
            )

            msg.submit(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, status, last_message, plot],
            )

            clear_btn.click(
                fn=clear_history,
                inputs=[],
                outputs=[chatbot, msg, status, last_message, plot],
            )

            retry_btn.click(
                fn=retry_last_message,
                inputs=[chatbot],
                outputs=[chatbot, msg, status, last_message, plot],
            )

        return demo


def build_gradio_app() -> gr.Blocks:
    """
    Build and return the Gradio application

    Returns:
        gr.Blocks: The Gradio interface
    """
    chat_api = ChatAPI(BASE_URL, API_KEY)
    chat_interface = ChatInterface(chat_api)
    return chat_interface.demo
