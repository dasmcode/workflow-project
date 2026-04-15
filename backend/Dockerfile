FROM python:3.14-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y gosu curl && \
    curl -Ls https://astral.sh/uv/install.sh | sh && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"
RUN groupadd -g 10000 appgroup && useradd -m -u 10000 -g appgroup appuser
RUN mkdir -p /appuser && chown -R appuser:appgroup /appuser
WORKDIR /appuser
COPY pyproject.toml uv.lock ./
RUN uv pip install --system .
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"
EXPOSE 8000
RUN rm -rf /root/.local
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY --chown=appuser:appgroup . .
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
