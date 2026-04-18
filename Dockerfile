FROM python:3.14-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr libtesseract-dev tesseract-ocr-eng libleptonica-dev pkg-config build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
WORKDIR /app
COPY requirements.txt .
RUN uv init && \
    uv add -r requirements.txt --index-strategy unsafe-best-match

FROM python:3.14-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_DEV=1 \
    UV_TOOL_BIN_DIR=/usr/local/bin 
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y --no-install-recommends \
    gosu libgl1 libglib2.0-0 libxcb1 libx11-6 libsm6 libxext6 libxrender1 tesseract-ocr libtesseract-dev tesseract-ocr-eng libleptonica-dev pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN groupadd -g 10000 appgroup && useradd -m -u 10000 -g appgroup appuser
RUN mkdir -p /appuser && chown -R appuser:appgroup /appuser
WORKDIR /appuser
COPY --from=builder /app/uv.lock uv.lock
COPY --from=builder /app/pyproject.toml pyproject.toml
RUN uv sync --locked --no-install-project