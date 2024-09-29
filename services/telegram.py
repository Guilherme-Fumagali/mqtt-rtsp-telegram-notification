import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def send_video(filename, caption):
    try:
        await bot.send_video(chat_id=BOT_CHAT_ID, video=FSInputFile(filename), caption=caption, request_timeout=120)
    except Exception as e:
        print(f"Error sending video: {e}")
        raise e
