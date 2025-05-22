---
title: OpenAI compatible Chatbot API
emoji: 🤯
colorFrom: pink
colorTo: yellow
sdk: docker
pinned: false
short_description: OpenAI compatible Chatbot API
---

[HF URL](https://huggingface.co/spaces/lokumai/openai-openapi-template)
[HF_APP_URL](https://lokumai-openai-openapi-template.hf.space/)
[Github URL](https://github.com/lokumai/openai-openapi-template)


# OpenAI Compatible Chatbot API

A FastAPI based OpenAI compatible Chatbot API with Visualization.


## 🚀 Features

- OpenAI compatible API /v1/chat/completions
- Complete mock implementation with USE_MOCK_API environment variable
- Secure API key generation with HMAC signatures and API key authentication
- In-memory storage for chat history and plots for mock implementation
- MongoDB storage for chat history and plots for production
- Support for all major OpenAI API endpoints




## 📋 Endpoints
- GET     - `/chat/completions` list stored chat completions - for first load the chatbot
- POST    - `/chat/completions` create a new chat completion - when user starts a new chat
- GET     - `/chat/completions/{completion_id}` get a stored chat completion by completion_id - when user clicks on a chat on the list
- POST    - `/chat/completions/{completion_id}` modify a stored chat completion by completion_id - NOT IMPLEMENTED YET
- DELETE  - `/chat/completions/{completion_id}` delete a stored chat completion by completion_id - NOT IMPLEMENTED YET
- GET     - `/chat/completions/{completion_id}/messages` get the messages in a stored chat completion by completion_id - when user clicks on a chat on the list
- GET     - `/chat/completions/{completion_id}/messages/{message_id}/plots` get the plots/graph-data/figure-json in a stored chat completion by completion_id and message_id


## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/lokumai/openai-openapi-template.git
```

2. Install dependencies:
```bash
uv sync
```

3. Run the server:
```bash
uv run uvicorn app:app --reload
```