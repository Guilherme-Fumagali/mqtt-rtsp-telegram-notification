from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _split_env(name: str) -> list[str]:
    val = os.getenv(name, "").strip()
    if not val:
        return []
    return [p.strip() for p in val.split(',') if p.strip()]


@dataclass(slots=True)
class Config:
    mqtt_host: str | None = os.getenv("MQTT_HOST")
    mqtt_user: str | None = os.getenv("MQTT_USERNAME")
    mqtt_pass: str | None = os.getenv("MQTT_PASSWORD")
    mqtt_topic: str | None = os.getenv("MQTT_TOPIC")

    rtsp_urls: List[str] = field(default_factory=lambda: _split_env("RTSP_URLS"))
    camera_labels_env: List[str] = field(default_factory=lambda: _split_env("RTSP_LABELS"))

    ffmpeg_input_args: str = os.getenv("FFMPEG_INPUT_ARGS")
    ffmpeg_output_args: str = os.getenv("FFMPEG_OUTPUT_ARGS")
    ffmpeg_compress_args: str = os.getenv("FFMPEG_COMPRESS_ARGS")

    video_tmp_dir: str = os.getenv("VIDEO_TMP_DIR") or "."

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    bot_token: str | None = os.getenv("BOT_TOKEN")
    bot_chat_id: str | None = os.getenv("BOT_CHAT_ID")

    gotify_url: str | None = os.getenv("GOTIFY_URL")
    gotify_token: str | None = os.getenv("GOTIFY_TOKEN")

    def __post_init__(self):
        if not self.mqtt_host:
            raise ValueError("MQTT_HOST is required")
        if not self.mqtt_topic:
            raise ValueError("MQTT_TOPIC is required")
        if not self.rtsp_urls:
            raise ValueError("At least one RTSP_URLS is required")
        if not self.ffmpeg_input_args:
            raise ValueError("FFMPEG_INPUT_ARGS is required")
        if not self.ffmpeg_output_args:
            raise ValueError("FFMPEG_OUTPUT_ARGS is required")
        if self.bot_token and not self.bot_chat_id:
            raise ValueError("BOT_CHAT_ID is required when BOT_TOKEN is set")
        if self.gotify_token and not self.gotify_url:
            raise ValueError("GOTIFY_URL is required when GOTIFY_TOKEN is set")

    @property
    def camera_labels(self) -> list[str]:
        if not self.camera_labels_env:
            return [f"Cam{i+1}" for i in range(len(self.rtsp_urls))]
        labels = self.camera_labels_env[:len(self.rtsp_urls)]
        if len(labels) < len(self.rtsp_urls):
            labels.extend([f"Cam{i+1}" for i in range(len(labels), len(self.rtsp_urls))])
        return labels

    def to_dict_redacted(self) -> dict:
        return {
            "mqtt_host": self.mqtt_host,
            "mqtt_user": "***" if self.mqtt_user else None,
            "mqtt_pass": "***" if self.mqtt_pass else None,
            "mqtt_topic": self.mqtt_topic,
            "rtsp_urls": ["***" for _ in self.rtsp_urls],
            "camera_labels": self.camera_labels,
            "ffmpeg_input_args": self.ffmpeg_input_args,
            "ffmpeg_output_args": self.ffmpeg_output_args,
            "ffmpeg_compress_args": self.ffmpeg_compress_args,
            "video_tmp_dir": self.video_tmp_dir,
            "log_level": self.log_level,
            "bot_token": "***" if self.bot_token else None,
            "bot_chat_id": self.bot_chat_id,
            "gotify_url": self.gotify_url,
            "gotify_token": "***" if self.gotify_token else None,
        }
