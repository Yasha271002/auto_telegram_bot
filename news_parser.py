import feedparser
import logging
import ssl
import re

from deduplicator import is_duplicate
from image_finder import get_image_from_url

ssl._create_default_https_context = ssl._create_unverified_context
logger = logging.getLogger(__name__)

KEYWORDS = [
    "Tesla", "BMW", "Mercedes", "electric", "EV",
    "Lamborghini", "Ferrari", "Audi", "Porsche", "Rivian", "Lucid",
    "Nissan", "Chevrolet", "Ford", "Mustang", "F-150", "Cybertruck",
    "autonomous", "self-driving", "autopilot", "FSD", "Full Self-Driving",
    "Lada", "GAZ", "UAZ", "KAMAZ", "AvtoVAZ", "ZIL", "URAL", "Volga", "Zhiguli",
    "Лада", "ГАЗ", "УАЗ", "КАМАЗ", "АвтоВАЗ", "ЗИЛ", "УРАЛ", "Волга", "Жигули"
]

def load_rss():
    try:
        with open("rss.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"❌ Ошибка чтения RSS: {e}")
        return []

def filter_trending(news_list):
    filtered = []

    for news in news_list:
        if any(k.lower() in news["title"].lower() for k in KEYWORDS):
            logger.info(f"🔥 Трендовых новостей: {len(filtered)}")
            filtered.append(news)
        
        if len(filtered) == 0:
            logger.info(f"Трендовых новостей не найдено, беру обычные новости: {len(filtered)}")
            filtered = news_list[:5]

    return filtered

def extract_image(entry):
    if "media_content" in entry:
        return entry.media_content[0].get("url")

    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                return link.get("href")

    if "summary" in entry:
        match = re.search(r'<img.*?src="(.*?)"', entry.summary)
        if match:
            return match.group(1)

    return None


def get_latest_news(limit=5):
    news_list = []
    feeds = load_rss()

    if not feeds:
        logger.warning("⚠️ Нет RSS источников")
        return []
    

    for url in feeds:
        logger.info(f"📡 Парсим: {url}")
        feed = feedparser.parse(url)

        for entry in feed.entries[:limit]:
            if is_duplicate(entry.title):
                continue
            
            image = extract_image(entry)
            if not image:
                image = get_image_from_url(entry.link)

            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "image": image
                
            })

    logger.info(f"📰 Найдено новостей: {len(news_list)}")
    
    return news_list