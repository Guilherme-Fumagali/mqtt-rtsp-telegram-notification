FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

ARG TZ=UTC
ENV TZ=${TZ}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    ffmpeg \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

ARG APP_USER=app
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER}

COPY --chown=${APP_USER}:${APP_USER} . .

USER ${APP_USER}

ENTRYPOINT ["python", "door_open_monitor.py"]
