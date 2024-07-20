import asyncio
import os
from datetime import datetime

import aiomqtt as mqtt
import ffmpeg
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")
RTSP_URL = os.getenv("RTSP_URL")
VIDEO_TIME = os.getenv("VIDEO_TIME", default=10)
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

    try:
        (ffmpeg.input(RTSP_URL, **args)
         .output('video.mp4', format='mp4', t=VIDEO_TIME)
         .overwrite_output()
         .run())
    except Exception as e:
        print(f"Error generating video: {e}")
        print("Removing video file...")
        os.remove("video.mp4")


async def send_message():
    try:
        await bot.send_message(BOT_CHAT_ID, f"Portão aberto!\nData: {datetime.now()}", request_timeout=10)
        if os.path.exists("video.mp4"):
            await bot.send_video(chat_id=BOT_CHAT_ID, video=FSInputFile("video.mp4"), request_timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")


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


