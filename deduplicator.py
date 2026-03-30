import hashlib

FILE = "seen_news.txt"


def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()


def is_duplicate(text):
    h = hash_text(text.lower().strip())

    try:
        with open(FILE, "r") as f:
            hashes = f.read().splitlines()[-1000:]
    except:
        hashes = []

    if h in hashes:
        return True

    with open(FILE, "a") as f:
        f.write(h + "\n")

    return False