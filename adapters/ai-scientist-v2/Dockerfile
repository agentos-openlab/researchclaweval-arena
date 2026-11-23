FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim@sha256:7936cc6625ca04cafa6ecc3c2881ddfe90a747c55c74480cd4ac6ffad6a5af1e
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgomp1 \
    poppler-utils chktex texlive-latex-extra texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/framework
COPY . .
ENV PYTHONPATH=/opt/framework PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN uv pip install --system --index https://download.pytorch.org/whl/cpu 'torch==2.7.1' \
    && uv pip install --system -r requirements.txt 'psutil==7.0.0' 'PyYAML==6.0.2' \
    'scikit-learn==1.7.2' 'pandas==2.3.3' 'scipy==1.16.3' \
    && python launch_scientist_bfts.py --help >/dev/null
