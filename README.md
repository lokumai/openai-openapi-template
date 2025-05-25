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

- OpenAI compatible API 
     - /v1/chat/completions
     - /v1/chat/completions/{completion_id}
     - /v1/chat/completions/{completion_id}/messages
     - /v1/chat/completions/{completion_id}/messages/{message_id}/plots
     - /v1/conversation
     - /v1/conversation/{completion_id}

- Complete mock implementation with USE_MOCK_API environment variable
- Secure API key generation with HMAC signatures and API key authentication
- In-memory storage for chat history and plots for mock implementation
- MongoDB storage for chat history and plots for production
- Support for all major OpenAI API endpoints
- Gradio UI for testing the chatbot : [http://127.0.0.1:7860/ui](http://127.0.0.1:7860/ui)


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

2. Create a .env file in the root directory and add the following variables:
```bash
cp .env.example .env
```
* Set your own values for the variables in the .env file.

3. Install dependencies:
```bash
uv sync
```

4. Start MongoDB:
```bash
docker compose -f docker/mongodb-docker-compose.yaml up -d
```

5. Run API and Gradio UI on your local machine:
```bash

./run.sh

# or

uv run uvicorn main:app --host 0.0.0.0 --port 7860 --reload
```

## Usage

### 🔑 API Key Generation

```bash
./scripts/generate_api_key.sh <username> <secret_key>
```

* This will generate a API_KEY and save it to the api_key.txt file.
```plaintext
API Key generated:
Username: template
API Key: sk-template-token

API Key saved to api_key.txt
```

## 🔒 Security Configuration
There are various security configurations that can be set in the .env file for development and production environments.

- `SECURITY_ENABLED=True` or `False`, If security is enabled, the API will require an API_KEY to be provided in the request header.
- `SECURITY_DEFAULT_USERNAME=admin`, If security is disabled, the API will not require an API_KEY to be provided in the request header and will use this for current user.
- `SECURITY_SECRET_KEY=your-secret-key-here`, This is the secret key for the API_KEY generation. It is used to generate and verify the API_KEY for the user.
- `API_KEY`, If you want to use the Gradio UI, you can set the API_KEY in the .env file. GradioUI will use the API_KEY to make requests to the API. Especially `POST/chat/completions` endpoint.

### 🔑 API Key Authentication

```bash
curl -X POST "http://localhost:7860/v1/chat/completions" \
     -H "Authorization: Bearer sk-template-token" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## 💾 Embedded MongoDB for local machine development

* `database_type` environment variable is set to `embedded`, the API will use embedded MongoDB for local machine development. Default is `mongodb`.
* `mongodb_host` environment variable is set to `localhost`, the API will use localhost for MongoDB. Default is `localhost`.
* `mongodb_port` environment variable is set to `27017`, the API will use 27017 for MongoDB. Default is `27017`.
* `mongodb_database` environment variable is set to `openai_openapi_template`, the API will use openai_openapi_template for MongoDB. Default is `openai_openapi_template`.


## 🤝 Contributing  Attention Please!!!
When you make changes to the code, please run the following commands to ensure the code is running on your local machine and formatted and linted correctly.

* Fork the repository
```bash
git clone https://github.com/yourname/openai-openapi-template.git
```

* cd to the project directory
```bash
cd openai-openapi-template
```

* Create a new branch
```bash
git checkout -b feature/new-feature
# or
git checkout -b bug/fix-issue
# or
git checkout -b hotfix/critical-fix
```

* Make your changes and commit them
```bash
git status
git add .
git commit -m "Add new feature"
```

* Push your changes to the branch
```bash
git push origin feature/new-feature
```

* Merge from main branch to your branch
```bash
git fetch origin main
git merge origin/main
```

* Validate the code is running on your local machine
```bash
uv run uvicorn app:app --reload
```

* Format and lint the code
```bash
ruff check --fix
```

```bash
ruff format
```

* Everything is working, create a pull request
```bash
git push origin feature/new-feature
```

* Create a pull request
```bash
gh pr create --base main --head feature/new-feature --title "Add new feature" --body "This PR adds a new feature to the project"
```

 ## Open Issue
 Mock Implementation:
 - [X] Implement Mock response for all endpoints
 - [X] Implement API-Key Authentication and validation in all endpoints

 Production Implementation:
 - [X] POST chat/completions - create a new chat completion
 - [X] GET  chat/completions - list stored chat completions
 - [X] GET  chat/completions/{completion_id} - get a stored chat completion by id
 - [X] GET  chat/completions/{completion_id}/messages - get the messages in a stored chat completion by id
 - [X] GET  chat/completions/{completion_id}/messages/{message_id}/plots - get the plots/graph-data/figure-json in a stored chat completion by id and message id
-  [X] GET  conversation - get all conversations
-  [X] GET  conversation/{completion_id} - get a conversation by completion_id





