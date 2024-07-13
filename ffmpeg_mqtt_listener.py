from datetime import datetime

import aiomqtt as mqtt
import ffmpeg

import asyncio
import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")
RTSP_URL = os.getenv("RTSP_URL")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def generate_video():
    args = {
        "rtsp_transport": "tcp",
        "flags": "low_delay",
        "fflags": "nobuffer",
    }

    (ffmpeg.input(RTSP_URL, **args)
     .output('video.mp4', format='mp4', t=10)
     .overwrite_output()
     .run())


async def send_message():
    await bot.send_message(BOT_CHAT_ID, f"Portão aberto!\nData: {datetime.now()}")
    await bot.send_video(chat_id=BOT_CHAT_ID, video=FSInputFile("video.mp4"))


async def main():
    async with mqtt.Client(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD) as client:
        await client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
        async for msg in client.messages:
            print(f"Received message: {msg.payload}")
            if msg.payload == b"open":
                print("Generating video...")
                generate_video()
                print("Sending message...")
                await send_message()
                print("Message sent!")


if __name__ == "__main__":
    asyncio.run(main())

