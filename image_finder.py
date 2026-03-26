import requests

def get_image_from_url(url):
    try:
        html = requests.get(url, timeout=5).text

        import re
        match = re.search(r'<meta property="og:image" content="(.*?)"', html)

        if match:
            return match.group(1)

    except:
        pass

    return None