FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    libgomp1 libgl1 ripgrep \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/framework
COPY . .
ENV PYTHONPATH=/opt/framework:/opt/framework/research_agent \
    PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 LITELLM_LOCAL_MODEL_COST_MAP=True
RUN printf 'torch==2.7.1\ntorchvision==0.22.1\n' > /tmp/torch-constraints.txt \
    && uv pip install --system --index https://download.pytorch.org/whl/cpu \
    'torch==2.7.1' 'torchvision==0.22.1' \
    && uv pip install --system --constraint /tmp/torch-constraints.txt \
    -e /opt/framework 'scikit-learn==1.7.2' \
    && python -c 'from research_agent.run_infer_idea import InnoFlow'
