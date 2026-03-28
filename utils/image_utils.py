import requests
from bs4 import BeautifulSoup


def get_full_image(url):
    try:
        r = requests.get(url, timeout=5, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(r.text, "html.parser")

        img = soup.find("meta", property="og:image")
        if img and img.get("content"):
            return img["content"]
    except:
        pass

    return None


def improve_image_url(url: str) -> str:
    if not url:
        return None

    url = url.replace("-300x200", "")
    url = url.replace("-150x150", "")
    url = url.replace("small", "large")
    url = url.replace("thumb", "full")

    return url


def get_fallback_image(title: str):
    return f"https://source.unsplash.com/800x600/?car,{title}"


def get_best_image(news: dict):
    
    image = get_full_image(news.get("link"))

    if not image:
        image = improve_image_url(news.get("image"))

    if not image:
        image = get_fallback_image(news.get("title", "car"))

    return image