import gradio as gr
import environs
import httpx
import asyncio

env = environs.Env()
env.read_env()

BASE_URL = env.str("BASE_URL", "http://localhost:7860")
API_KEY = env.str("API_KEY", "sk-test-xxx")
CHAT_API_ENDPOINT = f"{BASE_URL}/v1/chat/completions"

async def call_chat_api(prompt):
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
                return f"API Hatası: {response.text}"
            
            result = response.json()
            print(f"API response: {result}")
            
            # API yanıt yapısına göre içeriği al
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                return message.get("content", "Yanıt içeriği bulunamadı")
            else:
                return "Geçersiz API yanıtı"
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Bir hata oluştu: {str(e)}"

def build_gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("## Talk to your Data Chatbot")

        with gr.Row():
            prompt_input = gr.Textbox(label="Your Message", lines=3)
            output_text = gr.Textbox(label="Model Response", lines=3)

        async def on_submit(prompt):
            if not prompt.strip():
                return "Lütfen bir mesaj girin."
            return await call_chat_api(prompt)

        submit_btn = gr.Button("Send")
        submit_btn.click(
            fn=on_submit,
            inputs=[prompt_input],
            outputs=[output_text]
        )
        
        prompt_input.submit(
            fn=on_submit,
            inputs=[prompt_input],
            outputs=[output_text]
        )

    return demo

if __name__ == "__main__":
    demo = build_gradio_app()
    demo.launch(server_name="0.0.0.0", server_port=7861)
