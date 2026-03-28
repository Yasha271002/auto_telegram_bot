import feedparser
import logging
import ssl
import re

from utils.keywords import load_keywords
from deduplicator import is_duplicate
from image_finder import get_image_from_url

ssl._create_default_https_context = ssl._create_unverified_context
logger = logging.getLogger(__name__)

def load_rss():
    try:
        with open("rss.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"❌ Ошибка чтения RSS: {e}")
        return []

def filter_trending(news_list):
    filtered = []
    keywords = load_keywords()

    if not keywords:
        return news_list
    
    for news in news_list:
        text = (news["title"] + " " + news.get("summary", "")).lower()

        if any(k in text for k in keywords):
            filtered.append(news)

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