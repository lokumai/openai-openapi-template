import gradio as gr
import environs
import httpx
import asyncio
from typing import List, Tuple

env = environs.Env()
env.read_env()

BASE_URL = env.str("BASE_URL", "http://localhost:7860")
API_KEY = env.str("API_KEY", "sk-test-xxx")
CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"

async def call_chat_api(prompt: str) -> Tuple[str, str]:
    print(f"Calling chat API with prompt: {prompt}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                CHAT_API_ENDPOINT,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "gpt-3.5-turbo",
                    "completion_id": "new_chat",
                    "stream": True
                }
            )
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                return "Error", f"API Error: {response.text}"
            
            result = response.json()
            print(f"API response: {result}")
            
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                content = message.get("content", "Content not found")
                print(f"Last message: {content}")
                return "Success", content
            else:
                return "Error", "Invalid API response"
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Error", f"Error: {str(e)}"

def build_gradio_app():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🤖 Data Chatbot
        
        This chatbot allows you to chat with your data and visualize it.
        Please enter your question in the text box below and click the "Send" button.
        """)
        
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_copy_button=True,
                    avatar_images=("👤", "🤖")
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Enter your question here...",
                        lines=3,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
                    retry_btn = gr.Button("Retry", variant="secondary")
                
                status = gr.Textbox(label="Status", interactive=False)
                last_message = gr.Textbox(label="Last Message", interactive=False)
        
        async def user_message(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str, str, str]:
            if not message.strip():
                return history, "", "Please enter a message.", ""
            
            history.append([message, ""])
            status_text, response = await call_chat_api(message)
            
            if status_text == "Success":
                history[-1][1] = response
                return history, "", "Message sent successfully.", response
            else:
                history[-1][1] = f"❌ {response}"
                return history, "", f"Error: {response}", ""
        
        def clear_history() -> Tuple[List[List[str]], str, str, str]:
            return [], "", "Chat cleared.", ""
        
        def retry_last_message(history: List[List[str]]) -> Tuple[List[List[str]], str, str, str]:
            if not history:
                return history, "", "No message to retry.", ""
            
            last_message = history[-1][0]
            return history[:-1], last_message, "Last message will be retried.", ""
        
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

if __name__ == "__main__":
    demo = build_gradio_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
