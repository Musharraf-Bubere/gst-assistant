FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Hugging Face Spaces runs containers as user 1000, so build as that user from the start.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FASTEMBED_CACHE_PATH=/home/user/.fastembed
RUN mkdir -p /home/user/app/data/processed
WORKDIR /home/user/app

COPY --chown=user pyproject.toml uv.lock .python-version README.md ./
RUN uv sync --locked --no-install-project --no-dev

COPY --chown=user app.py ./
COPY --chown=user gst_assistant ./gst_assistant
COPY --chown=user data/processed/records.json ./data/processed/records.json

# Download the embedding model and build the vector file now, so start-up is fast.
RUN uv run --no-sync python -c "from gst_assistant.domains.gst.answer import Searcher, load_records; Searcher(load_records())"

EXPOSE 8501

CMD [".venv/bin/streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
