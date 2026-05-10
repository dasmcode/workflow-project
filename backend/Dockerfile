FROM workflow-template:v1.1
RUN ln -s $(dpkg -L tesseract-ocr-eng | grep tessdata$) /usr/local/share/tessdata_link
ENV TESSDATA_PREFIX=/usr/local/share/tessdata_link
COPY --chown=appuser:appgroup . .
RUN mkdir -p /appuser/uploads && chown appuser:appgroup /appuser/uploads
RUN mkdir -p /tmp/prometheus && chown appuser:appgroup /tmp/prometheus
RUN uv sync --locked --no-install-project
EXPOSE 8000
ENV PATH="/appuser/.venv/bin:$PATH"
USER appuser
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

