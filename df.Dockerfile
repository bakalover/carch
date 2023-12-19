FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  POETRY_VERSION=1.6.1

WORKDIR /lab
COPY ./poetry.lock ./pyproject.toml /lab

RUN pip install --no-c  ache-dir --progress-bar off "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false \
  && poetry install --no-cache --no-interaction --no-ansi
