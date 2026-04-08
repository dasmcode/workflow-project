FROM python:3.12 AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    cargo \
    rustc \
    ca-certificates \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
COPY requirements.txt .
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN groupadd -g 10000 appgroup && useradd -m -u 10000 -g appgroup appuser
RUN mkdir -p /appuser && chown -R appuser:appgroup /appuser
WORKDIR /appuser
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"
RUN pip uninstall -y pip setuptools wheel
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY --chown=appuser:appgroup . .
ENTRYPOINT ["/entrypoint.sh"]
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]