FROM python:3.11.13-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /arena
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /tmp/requirements.txt \
    && python -c 'import datasets, pyarrow, whestbench'
