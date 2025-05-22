# gradio.py
import gradio as gr
import asyncio
import httpx
import environs

env = environs.Env()
env.read_env()

BASE_URL = env.str("BASE_URL", "http://localhost:7860")
API_KEY = env.str("API_KEY", "sk-test-xxx")

CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"

async def call_chat_api(user_input):
    headers = {"Authorization": f"sk-{API_KEY}"}
    payload = {
        "messages": [{"role": "user", "content": user_input}]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(CHAT_API_ENDPOINT, json=payload, headers=headers)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

def chatbot_fn(user_input):
    return asyncio.run(call_chat_api(user_input))

def launch_gradio():
    iface = gr.Interface(fn=chatbot_fn, inputs="text", outputs="text", title="Chat with your Data")
    iface.launch(server_name="0.0.0.0", server_port=7861, show_error=True)
