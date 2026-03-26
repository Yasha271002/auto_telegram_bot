import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID
from poster import send_post
from scheduler import start_scheduler
from ai_generator import generate_news_posts
from logger import setup_logger
from rss_manager import add_rss, remove_rss, get_rss_list
import logging

setup_logger()
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("listrss"))
async def cmd_list_rss(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    feeds = get_rss_list()

    if not feeds:
        await message.reply("❌ Список пуст")
        return

    text = "📡 RSS источники:\n\n"
    text += "\n".join(feeds)

    await message.reply(text)

@dp.message(Command("removerss"))
async def cmd_remove_rss(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        url = message.text.split(" ")[1]
    except:
        await message.reply("❌ Используй: /removerss URL")
        return

    if remove_rss(url):
        await message.reply("🗑 Удалено")
    else:
        await message.reply("⚠️ Не найдено")

@dp.message(Command("addrss"))
async def cmd_add_rss(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        url = message.text.split(" ")[1]
    except:
        await message.reply("❌ Используй: /addrss https://site.com/rss")
        return

    result = add_rss(url)

    if result == True:
        await message.reply("✅ RSS добавлен")
    elif result == "invalid":
        await message.reply("❌ Это невалидный RSS")
    else:
        await message.reply("⚠️ Уже есть")

@dp.message(Command("post"))
async def manual_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    topic = message.text.replace("/post", "").strip()
    if not topic:
        await message.answer("Использование: /post Тема поста")
        return

    await message.answer("🤖 Генерирую пост...")
    text = await generate_news_posts(topic)
    await send_post(bot, text)
    await message.answer("✅ Пост отправлен в канал!")

async def main():
    logger.info("🚀 Бот запускается...")
    
    await start_scheduler(bot)
    logger.info("✅ Scheduler запущен")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())