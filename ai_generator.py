from openai import AsyncOpenAI
from dotenv import load_dotenv
from news_parser import get_latest_news, filter_trending
from utils.image_utils import get_best_image
from rss_manager import add_rss
from deduplicator import is_duplicate

import logging
import os
import re

load_dotenv()

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                     base_url="https://api.aitunnel.ru/v1")

MODEL = "deepseek-chat"

async def rewrite_news(title: str, link: str):
    prompt = f"""
        Ты делаешь вирусные посты для Telegram (авто-тематика).

        Новость: {title}

        Сделай:
        - краткий пересказ новости (не больше 30 строк)
        - мощный заголовок
        - эмоции (🔥 ⚡ 😳)
        - ощущение срочности или эксклюзива
        - стиль как у популярных каналов

        Без воды. Максимум вовлечения.

        - в конце добавь:
        👉 Читать: {link}
        """

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    return response.choices[0].message.content.strip()

async def generate_news_posts():
    news = get_latest_news(limit=10)
    news = filter_trending(news)

    if not news:
        print("⚠️ Новостей нет — ищу новые RSS")

        added = await find_new_rss_sources()
        print(f"➕ Добавлено RSS: {added}")

        news = get_latest_news(limit=10)
        news = filter_trending(news)

        if not news:
            print("❌ Даже после обновления RSS новостей нет")
            return []

    posts = []

    for item in news:
        if is_duplicate(item["title"] + item["link"]):
            continue

        text = await rewrite_news(item["title"], item["link"])
        image = get_best_image(item)

        posts.append({
            "text": text,
            "image": image
        })

    return posts

async def find_new_rss_sources():
    prompt = """
        Найди 15 сайтов с автоновостями и дай ТОЛЬКО RSS ссылки.
        Только реальные RSS (которые открываются и содержат новости)
        
        Формат ответа:
        https://site.com/rss
        https://example.com/feed

        Без текста.
        """

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    urls = re.findall(r'https?://[^\s]+', response.choices[0].message.content)
    added = 0

    for url in urls:
        result = add_rss(url)

        if result == True:
            added += 1

    return added