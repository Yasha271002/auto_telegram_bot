import logging
import asyncio
import settings

from random import random
from user_content import save_user_post
from email.message import Message
from storage import get_all_posts, get_posts_count, delete_post_by_index, get_posts_titlesadd_my_post, get_post, get_my_post
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_TOKEN, ADMIN_ID
from poster import send_post
from scheduler import start_scheduler
from ai_generator import generate_news_posts
from logger import setup_logger
from utils.keywords import add_keyword, remove_keyword, load_keywords
from rss_manager import add_rss, remove_rss, get_rss_list
from router import route
from filters import add_filter, remove_filter, load_filters, smart_filter

setup_logger()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Подобрать авто")],
        [KeyboardButton(text="⚖️ Сравнить авто")],
        [KeyboardButton(text="🧠 Стоит ли брать")],
        [KeyboardButton(text="🔥 Новости")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Выбери действие 👇", reply_markup=kb)

@dp.message(lambda m: m.text == "🚗 Подобрать авто")
async def podbor_btn(message: types.Message):
    await message.answer("Напиши бюджет и требования\n\nНапример: до 1 млн седан")


@dp.message(lambda m: m.text == "⚖️ Сравнить авто")
async def compare_btn(message: types.Message):
    await message.answer("Напиши: Camry vs Accord")


@dp.message(lambda m: m.text == "🧠 Стоит ли брать")
async def buy_btn(message: types.Message):
    await message.answer("Напиши модель авто\n\nНапример: BMW 3 2018")

@dp.message()
async def ai_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return

    text = message.text

    if not await smart_filter(text):
        await message.answer(
            "🚗 Я разбираюсь только в авто.\n\n"
            "Попробуй:\n"
            "• Подбери авто до 1 млн\n"
            "• Camry vs Accord\n"
            "• Стоит ли брать BMW"
        )
        return

    await message.answer("🤖 Думаю...")

    result = await route(text)

    result += "\n\n👉 Подпишись на канал с новостями"

    await message.answer(result)

    if len(result) > 200 and random.random() < 0.3:
        save_user_post(text, result)

@dp.message(Command("posts"))
async def cmd_posts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    posts = get_all_posts()

    if not posts:
        await message.answer("❌ Кэш пуст")
        return

    for i, post in enumerate(posts[:20]):
        title = post.get("text", "")[:60].replace("\n", " ")

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Удалить",
                        callback_data=f"del_{i}"
                    )
                ]
            ]
        )

        await message.answer(f"{i}. {title}...", reply_markup=kb)

@dp.message(Command("countposts"))
async def cmd_count_posts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    count = get_posts_count()
    await message.answer(f"📦 Всего постов: {count}")

@dp.message(Command("deletepost"))
async def cmd_delete_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        index = int(message.text.split()[1])
    except:
        await message.answer("❌ Пример: /deletepost 2")
        return

    deleted = delete_post_by_index(index)

    if not deleted:
        await message.answer("❌ Нет такого поста")
        return

    title = deleted.get("text", "")[:50]

    await message.answer(f"🗑 Удалён:\n{title}...")

@dp.callback_query(lambda c: c.data.startswith("del_"))
async def delete_post_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    index = int(callback.data.split("_")[1])

    deleted = delete_post_by_index(index)

    if not deleted:
        await callback.answer("❌ Уже удалён", show_alert=True)
        return

    await callback.message.edit_text("🗑 Удалено")
    await callback.answer("Удалено")

@dp.message(Command("addfilter"))
async def cmd_add_filter(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    word = message.text.replace("/addfilter", "").strip()

    if not word:
        await message.answer("❌ Напиши слово")
        return

    if add_filter(word):
        await message.answer(f"✅ Добавлено: {word}")
    else:
        await message.answer("⚠️ Уже есть")

@dp.message(Command("removefilter"))
async def cmd_remove_filter(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    word = message.text.replace("/removefilter", "").strip()

    if not word:
        await message.answer("❌ Напиши слово")
        return

    if remove_filter(word):
        await message.answer(f"🗑 Удалено: {word}")
    else:
        await message.answer("⚠️ Не найдено")

@dp.message(Command("listfilter"))
async def cmd_list_filter(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    filters = load_filters()

    if not filters:
        await message.answer("❌ Фильтр пуст")
        return

    text = "📋 Фильтр:\n\n" + "\n".join(filters)

    await message.answer(text)

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