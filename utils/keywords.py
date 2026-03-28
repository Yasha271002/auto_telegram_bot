import os

FILE = "keywords.txt"


def load_keywords():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def save_keywords(keywords):
    with open(FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(set(keywords)))


def add_keyword(keyword: str):
    keywords = load_keywords()
    keyword = keyword.lower()

    if keyword in keywords:
        return False

    keywords.append(keyword)
    save_keywords(keywords)
    return True


def remove_keyword(keyword: str):
    keywords = load_keywords()
    keyword = keyword.lower()

    if keyword not in keywords:
        return False

    keywords.remove(keyword)
    save_keywords(keywords)
    return True