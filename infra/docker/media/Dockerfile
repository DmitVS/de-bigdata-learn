# Образ media: видео в стиле 3Blue1Brown для сложных тем курса.
#   Manim Community — анимация сцен на Python;
#   manim-voiceover — синхронизация анимации с озвучкой;
#   Piper — офлайн-синтез речи, русский голос Ruslan (модель встроена в образ).
# LaTeX не ставится: формулы не нужны, текст рисует Pango (кириллица — шрифт DejaVu).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential pkg-config libcairo2-dev libpango1.0-dev \
       ffmpeg sox fonts-dejavu curl \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} dev && useradd -m -u ${UID} -g ${GID} -s /bin/bash dev \
    && mkdir -p /opt/media-venv /opt/piper && chown dev:dev /opt/media-venv /opt/piper

USER dev
ENV VIRTUAL_ENV=/opt/media-venv PATH=/opt/media-venv/bin:$PATH UV_LINK_MODE=copy
COPY --chown=dev:dev requirements.txt /tmp/requirements.txt
RUN uv venv /opt/media-venv && uv pip install --no-cache -r /tmp/requirements.txt

# Голос Piper: ru_RU-ruslan-medium (модель ONNX и её конфиг)
ARG VOICE_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium
RUN curl -fsSL -o /opt/piper/ru_RU-ruslan-medium.onnx ${VOICE_URL}/ru_RU-ruslan-medium.onnx \
    && curl -fsSL -o /opt/piper/ru_RU-ruslan-medium.onnx.json ${VOICE_URL}/ru_RU-ruslan-medium.onnx.json
ENV PIPER_VOICE=/opt/piper/ru_RU-ruslan-medium.onnx

WORKDIR /workspace
