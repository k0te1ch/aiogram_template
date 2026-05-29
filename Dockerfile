FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    python -m pip install --upgrade poetry

# Install dependencies first for better layer caching.
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root

# Application source.
COPY . /app/

# Stage for running tests.
FROM base AS test
RUN poetry install --no-root
CMD ["poetry", "run", "pytest"]

# Final runtime image.
FROM base AS final
CMD ["python", "cli.py", "run"]
