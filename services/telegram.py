import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputMediaVideo

from services.config import Config

config = Config()

bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
logger = logging.getLogger(__name__)


async def send_video(filename, caption):
    try:
        logger.info("Enviando vídeo para Telegram", extra={"file": filename})
        await bot.send_video(chat_id=config.bot_chat_id, video=FSInputFile(filename), caption=caption, request_timeout=120)
        logger.info("Vídeo enviado com sucesso", extra={"file": filename})
    except Exception as e:
        logger.exception("Erro enviando vídeo para Telegram", extra={"file": filename})
        raise e


async def send_videos(filenames, caption):
    try:
        if not filenames:
            raise ValueError("Lista de vídeos vazia")
        if len(filenames) == 1:
            return await send_video(filenames[0], caption)
        original_count = len(filenames)
        if original_count > 10:
            logger.warning("Mais de 10 vídeos solicitados; truncando para 10 (limite Telegram)", extra={"total": original_count})
            filenames = filenames[:10]
        logger.info("Enviando grupo de vídeos", extra={"count": len(filenames)})
        media = []
        for i, f in enumerate(filenames):
            media.append(InputMediaVideo(media=FSInputFile(f), caption=caption if i == 0 else None))
        await bot.send_media_group(chat_id=config.bot_chat_id, media=media, request_timeout=180)
        logger.info("Grupo de vídeos enviado", extra={"count": len(filenames)})
    except Exception:
        logger.exception("Erro enviando grupo de vídeos", extra={"count": len(filenames)})
        raise
