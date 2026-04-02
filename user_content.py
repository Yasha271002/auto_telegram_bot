from storage import add_posts

def save_user_post(question, answer):
    text = f"""
🤔 Вопрос подписчика:
{question}

🤖 Ответ:
{answer}
"""

    add_posts([{
        "text": text.strip(),
        "image": None
    }])