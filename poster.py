from aiogram import Bot
from config import CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

async def send_post(bot, text, image=None):
    try:
        if image:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image,
                caption=text
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text
            )

        logger.info("📢 Пост отправлен")

    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")