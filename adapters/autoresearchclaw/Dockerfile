FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY . /opt/framework
RUN uv pip install --system -e /opt/framework 'httpx==0.28.1' 'torch==2.7.1' 'scikit-learn==1.7.2' \
    'pandas==2.3.3' 'pyarrow==21.0.0' 'matplotlib==3.10.7' 'scipy==1.16.3' \
    'transformers==4.55.4' 'datasets==3.6.0' 'gymnasium[classic-control]==1.1.1'
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN researchclaw --help >/dev/null
