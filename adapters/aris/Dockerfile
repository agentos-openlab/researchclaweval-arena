FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
ARG TARGETARCH
RUN test "$TARGETARCH" = amd64 && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git libgomp1 ripgrep \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/releases/download/v0.4.28/aris-code-linux-x64.tar.gz -o /tmp/aris.tar.gz \
    && printf '%s  %s\n' d29391a38c81fb6dcb01df3b607e8944d4f877355e39603a52d79bd22bab70f6 /tmp/aris.tar.gz | sha256sum -c - \
    && tar -xzf /tmp/aris.tar.gz -C /usr/local/bin aris \
    && rm /tmp/aris.tar.gz \
    && aris --version
COPY . /opt/framework
RUN uv pip install --system 'scikit-learn==1.7.2' 'pandas==2.3.3' \
    'numpy==2.2.6' 'scipy==1.16.3' 'matplotlib==3.10.7'
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ARIS_REPO=/opt/framework
