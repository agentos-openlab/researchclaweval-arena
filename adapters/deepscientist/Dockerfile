FROM node:24-trixie-slim@sha256:735dd688da64d22ebd9dd374b3e7e5a874635668fd2a6ec20ca1f99264294086 AS nodejs
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
COPY --from=nodejs /usr/local/bin/node /usr/local/bin/node
COPY --from=nodejs /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates libgomp1 ripgrep \
    && rm -rf /var/lib/apt/lists/*
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never \
    PATH="/opt/venv/bin:/opt/framework/node_modules/.bin:${PATH}" \
    DEEPSCIENTIST_REPO_ROOT=/opt/framework PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /opt/framework
COPY . .
RUN uv sync --frozen --no-dev \
    && uv pip install --python /opt/venv/bin/python 'scikit-learn==1.7.2' 'pandas==2.3.3' \
    'numpy==2.2.6' 'scipy==1.16.3' 'matplotlib==3.10.7' \
    && npm ci --omit=dev --no-audit --no-fund \
    && opencode --version \
    && ds run --help >/dev/null
