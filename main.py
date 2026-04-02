import logging
import asyncio
import settings

from email.message import Message
from storage import add_my_post,    get_post, get_my_post
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID
from poster import send_post
from scheduler import start_scheduler
from ai_generator import generate_news_posts
from logger import setup_logger
from utils.keywords import add_keyword, remove_keyword, load_keywords
from rss_manager import add_rss, remove_rss, get_rss_list
import logging

setup_logger()
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("startrss"))
async def start_rss(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    settings.RSS_AUTO_SEARCH = True
    await message.answer("✅ Автопоиск RSS включен")

@dp.message(Command("stoprss"))
async def stop_rss(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    settings.RSS_AUTO_SEARCH = False
    await message.answer("⛔ Автопоиск RSS остановлен")

@dp.message(Command("postnow"))
async def post_now(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # сначала твои посты
    post = get_my_post()

    if not post:
        post = get_post()

    if not post:
        await message.answer("❌ Нет постов в кэше")
        return

    await send_post(bot, post["text"], post.get("image"))

    await message.answer("🚀 Пост опубликован вручную")

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

@dp.message(Command("addkw"))
async def add_kw(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addkw", "").strip()

    if not text:
        await message.answer("❌ Напиши слово: /addkw tesla")
        return

    if add_keyword(text):
        await message.answer(f"✅ Добавлено: {text}")
    else:
        await message.answer("⚠️ Уже есть")

@dp.message(Command("removekw"))
async def remove_kw(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/removekw", "").strip()

    if not text:
        await message.answer("❌ Напиши слово: /removekw tesla")
        return

    if remove_keyword(text):
        await message.answer(f"🗑 Удалено: {text}")
    else:
        await message.answer("⚠️ Не найдено")

@dp.message(Command("keywords"))
async def list_kw(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    keywords = load_keywords()

    if not keywords:
        await message.answer("📭 Список пуст")
        return

    text = "📊 Ключевые слова:\n\n" + "\n".join(f"• {k}" for k in keywords)
    await message.answer(text)

@dp.message(Command("addpost"))
async def cmd_add_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/addpost", "").strip()

    if not text:
        await message.answer("❌ Напиши текст поста")
        return

    add_my_post(text)

    await message.answer("✅ Пост добавлен в очередь")

async def main():
    logger.info("🚀 Бот запускается...")
    
    await start_scheduler(bot)
    logger.info("✅ Scheduler запущен")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())