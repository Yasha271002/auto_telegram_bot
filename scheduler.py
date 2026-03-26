from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_generator import generate_news_posts
from poster import send_post
from storage import get_post, add_posts
from ai_generator import find_new_rss_sources

import random
import logging

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

TOPICS = [
    "новый Tesla Model Y 2026",
    "BMW M5 Touring 2026",
    "электрокары vs бензин",
]

async def auto_post(bot: Bot):
    try:
        logger.info("⏰ Запуск авто-поста")
        post = get_post()
        if not post:
            logger.info("❌ Нет постов — генерирую новую пачку")
            topic = random.choice(TOPICS)
            print("🧠 Генерирую пачку постов...")
            new_posts = await generate_news_posts()

            if not new_posts:
                logger.warning("⚠️ AI не дал посты — fallback")
                new_posts = [
                    {"text": f"🚗 {topic} — стоит ли брать?", "image": None},
                    {"text": f"🔥 {topic}: плюсы и минусы", "image": None},
                    {"text": f"⚡ Всё о {topic}", "image": None},
                        ]
                
            add_posts(new_posts)
            post = get_post()
        if not post:
            new_posts = await generate_news_posts()
            add_posts(new_posts)
            post = get_post()
        await send_post(bot, post["text"], post.get("image"))
        logger.info("✅ Пост опубликован")
        print("✅ Пост опубликован")

    except Exception as e:
        logger.error(f"❌ Ошибка автопоста: {e}")
        print("❌ Ошибка:", e)

async def start_scheduler(bot):
    scheduler.add_job(
        auto_post,
        'interval',
        seconds=3600, 
        args=[bot],
        id="auto_post_job",
        replace_existing=True
    )

    scheduler.add_job(
        find_new_rss_sources,
        trigger="interval",
        hours=24
    )
    scheduler.start()