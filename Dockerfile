FROM python:3.12 AS builder
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y --no-install-recommends build-essential ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
COPY requirements.txt .
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

FROM python:3.12-slim
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN groupadd -g 10000 appgroup && useradd -m -u 10000 -g appgroup appuser
RUN mkdir -p /app && chown -R appuser:appgroup /app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"
RUN pip uninstall -y pip setuptools wheel
EXPOSE 8000
COPY --chown=appuser:appgroup . .
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]