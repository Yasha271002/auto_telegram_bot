from ai_features import is_auto_question_ai

FILTER_FILE = "filters.txt"


def load_filters():
    try:
        with open(FILTER_FILE, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except:
        return []


def add_filter(word):
    word = word.lower().strip()

    filters = load_filters()[-500:]
    if word in filters:
        return False

    with open(FILTER_FILE, "a", encoding="utf-8") as f:
        f.write(word + "\n")

    return True

def remove_filter(word):
    word = word.lower().strip()
    filters = load_filters()[-500:]

    if word not in filters:
        return False

    filters.remove(word)

    with open(FILTER_FILE, "w", encoding="utf-8") as f:
        for w in filters:
            f.write(w + "\n")

    return True


def is_auto_fast(text):
    text = text.lower()
    filters = load_filters()[-500:]
    return any(word in text for word in filters)


def learn_from_text(text):
    words = text.lower().split()

    for word in words:
        if len(word) > 3 and word.isalpha():
            add_filter(word)


async def smart_filter(text):
    if is_auto_fast(text):
        return True

    is_auto = await is_auto_question_ai(text)

    if is_auto:
        learn_from_text(text)

    return is_auto