FROM python:3.11.13-slim-bookworm

RUN python -m pip install --no-cache-dir \
    numpy==2.2.6 jax==0.6.2 jaxlib==0.6.2 gymnax==0.0.9 \
    flax==0.10.7 optax==0.2.8 tensorflow-probability==0.25.0 \
    dotmap==1.3.30 PyYAML==6.0.2 tqdm==4.67.1 \
    && python -c 'import gymnax, jax, flax, optax; from tensorflow_probability.substrates import jax as tfp'
