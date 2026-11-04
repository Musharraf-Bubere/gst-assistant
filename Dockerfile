FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FASTEMBED_CACHE_PATH=/app/.fastembed

# Install the libraries first. This layer is reused unless pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock .python-version README.md ./
RUN uv sync --locked --no-install-project --no-dev

# Copy the application and the processed records (not the PDFs, logs, tests or secrets).
COPY app.py ./
COPY gst_assistant ./gst_assistant
COPY data/processed/records.json ./data/processed/records.json

# Download the embedding model and build the vector file now, so start-up is fast.
RUN uv run --no-sync python -c "from gst_assistant.domains.gst.answer import Searcher, load_records; Searcher(load_records())"

EXPOSE 8501

CMD ["uv", "run", "--no-sync", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
