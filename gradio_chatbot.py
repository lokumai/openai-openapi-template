import httpx
from fastapi import FastAPI
import gradio as gr
import environs

env = environs.Env()
env.read_env()

BASE_URL = env.str("BASE_URL", "http://localhost:7860")
API_KEY = env.str("API_KEY", "sk-test-xxx")
CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"


async def call_chat_api(prompt):
    return "Hello"
    headers = {"Authorization": API_KEY, "accept": "application/json"}
    payload = {"messages": [{"role": "user", "content": prompt}]}
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        response = await client.post(CHAT_API_ENDPOINT, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No content")
            )
        else:
            return f"Error {response.status_code}: {response.text}"


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("## Talk to your Data Chatbot")

        prompt_input = gr.Textbox(label="Your Message")
        output_text = gr.Textbox(label="Model Response")

        async def on_submit(prompt):
            return await call_chat_api(prompt)

        prompt_input.submit(on_submit, [prompt_input], output_text)
        gr.Button("Send").click(on_submit, [prompt_input], output_text)

    return demo


def mount_gradio(app: FastAPI, path: str = "/ui"):
    demo = build_gradio_app()
    app.mount(path, demo)
