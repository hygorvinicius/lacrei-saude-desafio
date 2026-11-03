FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app
RUN python -m pip install --no-cache-dir "poetry>=2.0,<3.0"

# O poetry.lock será usado automaticamente caso já tenha sido gerado e commitado.
COPY . /app
RUN poetry install --only main --no-root --no-interaction \
    && useradd --create-home appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app \
    && chmod +x /app/docker/entrypoint.sh

USER appuser
EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile - --error-logfile -"]
