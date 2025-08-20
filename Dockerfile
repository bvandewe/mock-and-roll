FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY poetry.lock pyproject.toml README.md /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY config/ /app/config/
COPY src/ /app/src/

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENV LOG_LEVEL="INFO"

RUN mkdir -p /app/logs && touch /app/logs/debug.log

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]