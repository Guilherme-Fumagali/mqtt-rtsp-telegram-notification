import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def send_video(video_buffer, caption):
    try:
        await bot.send_video(chat_id=BOT_CHAT_ID, video=video_buffer, caption=caption, request_timeout=10)
    except Exception as e:
        print(f"Error sending video: {e}")
        raise e
