import gradio as gr
import environs
import httpx
import asyncio
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Environment configuration
env = environs.Env()
env.read_env()

# API Configuration
BASE_URL = env.str("BASE_URL", "http://localhost:7860")
API_KEY = env.str("API_KEY", "sk-test-xxx")
CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"

class MessageStatus(Enum):
    """Enum for message status"""
    SUCCESS = "Success"
    ERROR = "Error"

@dataclass
class MessageResponse:
    """Data class for message response"""
    status: MessageStatus
    content: str
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
        print(f"Calling chat API with prompt: {prompt}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "model": "gpt-3.5-turbo",
                        "completion_id": "new_chat",
                        "stream": True
                    }
                )
                
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
                    return MessageResponse(
                        status=MessageStatus.ERROR,
                        content="",
                        error=f"API Error: {response.text}"
                    )
                
                result = response.json()
                print(f"API response: {result}")
                
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    content = message.get("content", "Content not found")
                    print(f"Last message: {content}")
                    return MessageResponse(
                        status=MessageStatus.SUCCESS,
                        content=content
                    )
                else:
                    return MessageResponse(
                        status=MessageStatus.ERROR,
                        content="",
                        error="Invalid API response"
                    )
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            return MessageResponse(
                status=MessageStatus.ERROR,
                content="",
                error=f"Error: {str(e)}"
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
        with gr.Blocks(theme=gr.themes.Soft()) as demo:
            # Header
            gr.Markdown(f"""
            # 🤖 Data Chatbot
            
            This chatbot allows you to chat with your data and visualize it.
            Please enter your question in the text box below and click the "Send" button.
            
            > 📚 API Documentation: [{self.chat_api.base_url}/docs]({self.chat_api.base_url}/docs)
            """)
            
            # Main chat interface
            with gr.Row():
                with gr.Column(scale=4):
                    # Chat history display
                    chatbot = gr.Chatbot(
                        label="Chat History",
                        height=400,
                        show_copy_button=True,
                        avatar_images=("👤", "🤖")
                    )
                    
                    # Message input area
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Enter your question here...",
                            lines=3,
                            scale=4
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
            async def user_message(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str, str, str]:
                """Handle user message submission"""
                if not message.strip():
                    return history, "", "Please enter a message.", ""
                
                history.append([message, ""])
                response = await self.chat_api.send_message(message)
                
                if response.status == MessageStatus.SUCCESS:
                    history[-1][1] = response.content
                    return history, "", "Message sent successfully.", response.content
                else:
                    history[-1][1] = f"❌ {response.error}"
                    return history, "", f"Error: {response.error}", ""
            
            def clear_history() -> Tuple[List[List[str]], str, str, str]:
                """Clear chat history"""
                return [], "", "Chat cleared.", ""
            
            def retry_last_message(history: List[List[str]]) -> Tuple[List[List[str]], str, str, str]:
                """Retry the last message"""
                if not history:
                    return history, "", "No message to retry.", ""
                
                last_message = history[-1][0]
                return history[:-1], last_message, "Last message will be retried.", ""
            
            # Connect event handlers to UI elements
            submit_btn.click(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, status, last_message]
            )
            
            msg.submit(
                fn=user_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg, status, last_message]
            )
            
            clear_btn.click(
                fn=clear_history,
                inputs=[],
                outputs=[chatbot, msg, status, last_message]
            )
            
            retry_btn.click(
                fn=retry_last_message,
                inputs=[chatbot],
                outputs=[chatbot, msg, status, last_message]
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

