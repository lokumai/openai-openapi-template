FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN useradd -m -u 1000 chameleon

USER chameleon

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

ENV PATH="/home/chameleon/.local/bin:$PATH"

WORKDIR /app

COPY --chown=chameleon pyproject.toml uv.lock ./

RUN uv sync --no-dev


COPY --chown=chameleon . /app

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Hugging Face Space port
ENV PORT=7860

# Expose the port
EXPOSE 7860

# Start command for Hugging Face Space
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
