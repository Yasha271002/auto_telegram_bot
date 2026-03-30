from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_generator import generate_news_posts
from poster import send_post
from storage import get_post, add_posts
from ai_generator import find_new_rss_sources

import logging

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

async def auto_post(bot: Bot):
    try:
        logger.info("⏰ Запуск авто-поста")

        post = get_post()

        if not post:
            logger.info("❌ Нет постов — генерирую новую пачку")

            new_posts = await generate_news_posts()

            if not new_posts:
                logger.warning("⚠️ Нет новостей — ищу новые RSS")

                added = await find_new_rss_sources()
                logger.info(f"➕ Добавлено RSS: {added}")

                new_posts = await generate_news_posts()

            if new_posts:
                add_posts(new_posts)
                post = get_post()

        if not post:
            logger.error("❌ Вообще нет постов даже после всех попыток")
            return

        await send_post(bot, post["text"], post.get("image"))

        logger.info("✅ Пост опубликован")

    except Exception as e:
        logger.error(f"❌ Ошибка автопоста: {e}")

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