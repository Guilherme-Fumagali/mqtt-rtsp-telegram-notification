import os

import requests

GOTIFY_URL = os.getenv("GOTIFY_URL")
GOTIFY_TOKEN = os.getenv("GOTIFY_TOKEN")


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
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending message to Gotify: {e}")
