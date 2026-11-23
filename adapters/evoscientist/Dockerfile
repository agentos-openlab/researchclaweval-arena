# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgomp1 ripgrep \
    && rm -rf /var/lib/apt/lists/*
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never \
    PATH="/opt/venv/bin:${PATH}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /opt/framework
COPY . .
RUN uv sync --frozen --no-dev --no-editable \
    && uv pip install --python /opt/venv/bin/python 'torch==2.7.1' 'scikit-learn==1.7.2' \
    'pandas==2.3.3' 'pyarrow==21.0.0' 'matplotlib==3.10.7' 'scipy==1.16.3' \
    'transformers==4.55.4' 'gymnasium[classic-control]==1.1.1' \
    && evosci --help >/dev/null
