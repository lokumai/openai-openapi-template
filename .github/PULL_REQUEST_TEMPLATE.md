---
name: Pull Request
about: Propose changes to the codebase
---

### 📝 Summary
Explain the purpose of your PR in 1-2 sentences.

### 🔧 Changes Made
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Dependency update
- [ ] AI-Agent
- [ ] LLM(Large Language Models)
- [ ] DWH(Data Warehouse)
- [ ] App Metadata
- [ ] MCP(Model Context Protocol)
- [ ] OpenAI API Compatibility
- [ ] OpenAPI/Swagger

### 🧪 Testing
- [ ] Git pull/merge the latest changes from the main branch
- [ ] `uv sync`
- [ ] Ran `ruff check --fix` and `ruff format`
- [ ] Validated with `uv run uvicorn main:app --reload`
- [ ] Tested via Gradio UI/Swagger/Postman/Curl

### 📚 Documentation
- [ ] Updated README.md
- [ ] Updated Swagger/OpenAPI docs
- [ ] Added docstrings to new code
- [ ] Changelog updated (if applicable)
- [ ] Inline comments added for complex logic
- [ ] Added example curl scripts for the new/updated API endpoints

### 🧩 Linked Issues
- Fixes #IssueNumber
- Resolves #IssueNumber

### 📌 Checklist
- [ ] I have read the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] My code follows Python style guide (PEP 8)
- [ ] My code adheres to global software standards:
  - ✅ **SOLID Principles** (Single Responsibility, Open/Closed, etc.)
  - ✅ **DRY (Don't Repeat Yourself)**
  - ✅ **KISS (Keep It Simple)**
  - ✅ **YAGNI (You Aren't Gonna Need It)**
- [ ] I have written meaningful commit messages