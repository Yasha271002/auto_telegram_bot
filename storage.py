import json
import os
import logging

FILE = "posts.json"
MY_POSTS_FILE = "my_posts.txt"

logger = logging.getLogger(__name__)

def load_posts():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_posts(posts):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def add_posts(new_posts):
    logger.info(f"📦 Добавляю {len(new_posts)} постов в кеш")
    posts = load_posts()
    posts.extend(new_posts)
    save_posts(posts)

def get_post():
    posts = load_posts()
    if not posts:
        logger.warning("⚠️ Кеш пуст")
        return None

    logger.info("📤 Беру пост из кеша")
    post = posts.pop(0)
    save_posts(posts)
    return post

def add_my_post(text):
    with open(MY_POSTS_FILE, "a", encoding="utf-8") as f:
        f.write(text.replace("\n", " ") + "\n")


def get_my_post():
    try:
        with open(MY_POSTS_FILE, "r", encoding="utf-8") as f:
            posts = f.readlines()
    except:
        return None

    if not posts:
        return None

    post = posts[0].strip()

    with open(MY_POSTS_FILE, "w", encoding="utf-8") as f:
        f.writelines(posts[1:])

    return {
        "text": post,
        "image": None
    }