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

## Contributing
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









### 🔑 API Key Authentication

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer sk-template-token" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'
```

 ## Open Issue
 - [ ] POST chat/completions - create a new chat completion
 - [ ] GET  chat/completions - list stored chat completions
 - [ ] GET  chat/completions/{completion_id} - get a stored chat completion by id
 - [ ] GET  chat/completions/{completion_id}/messages - get the messages in a stored chat completion by id
 - [ ] GET  chat/completions/{completion_id}/messages/{message_id}/plots - get the plots/graph-data/figure-json in a stored chat completion by id and message id
 - [ ] Implement Mock response for all endpoints
 - [ ] Implement API-Key Authentication and validation in all endpoints
 - [ ] 
 - [ ] 
