---
title: OpenAI compatible Chatbot API
emoji: 🤯
colorFrom: pink
colorTo: yellow
sdk: docker
pinned: false
short_description: OpenAI compatible Chatbot API
---

# OpenAI Compatible Chatbot API Template

A FastAPI based OpenAI compatible Chatbot API with Visualization.


## 🔗 Links
* [Github URL](https://github.com/lokumai/openai-openapi-template)
* [HF SPACE URL](https://huggingface.co/spaces/lokumai/openai-openapi-template)
* [SwaggerUI](https://lokumai-openai-openapi-template.hf.space/docs)
* [Redoc](https://lokumai-openai-openapi-template.hf.space/redoc)
* [OpenAPI](https://lokumai-openai-openapi-template.hf.space/openapi.json)


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

## Usage

### 🔑 API Key Generation

```bash
./scripts/api_key_generator.sh <username> <secret_key>
```

```text
API Key generated:
Username: template
API Key: sk-template-token

API Key saved to api_key.txt
```

### 🔑 API Key Authentication

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer sk-template-token" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'
```

 