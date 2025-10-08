import logging
import os

import requests

GOTIFY_URL = os.getenv("GOTIFY_URL")
GOTIFY_TOKEN = os.getenv("GOTIFY_TOKEN")

logger = logging.getLogger(__name__)


def send_gotify_message(title, message):
    if GOTIFY_URL and GOTIFY_TOKEN:
        try:
            response = requests.post(
                f"{GOTIFY_URL}/message",
                headers={"X-Gotify-Key": GOTIFY_TOKEN},
                json={
                    "title": title,
                    "message": message,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.debug("Mensagem Gotify enviada", extra={"title": title})
        except Exception:
            logger.exception("Erro enviando mensagem para Gotify", extra={"title": title})
    else:
        logger.debug("Gotify desabilitado - variáveis ausentes")
