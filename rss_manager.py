import feedparser
import logging

RSS_FILE = "rss.txt"
logger = logging.getLogger(__name__)


def validate_rss(url):
    try:
        feed = feedparser.parse(url)

        if not feed.entries:
            return False

        if not hasattr(feed.entries[0], "title"):
            return False

        return True
    except:
        return False

def get_rss_list():
    try:
        with open(RSS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []


def add_rss(url):
    feeds = get_rss_list()

    if url in feeds:
        return False

    if not validate_rss(url):
        return "invalid"

    with open(RSS_FILE, "a") as f:
        f.write(url + "\n")

    return True


def remove_rss(url):
    feeds = get_rss_list()

    if url not in feeds:
        return False

    feeds.remove(url)

    with open(RSS_FILE, "w") as f:
        for feed in feeds:
            f.write(feed + "\n")

    return True