FROM node:24-trixie-slim@sha256:735dd688da64d22ebd9dd374b3e7e5a874635668fd2a6ec20ca1f99264294086 AS nodejs
FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
COPY --from=nodejs /usr/local/bin/node /usr/local/bin/node
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates ripgrep libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY . /opt/framework
# The terminal chat uses Node's built-in modules. The model's experiment tools use Python.
RUN uv pip install --system 'scikit-learn==1.7.2' 'pandas==2.3.3' \
    'numpy==2.2.6' 'scipy==1.16.3' 'matplotlib==3.10.7' \
    && node /opt/framework/server/cli.js --version
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
