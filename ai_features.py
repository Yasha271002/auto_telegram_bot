from openai import AsyncOpenAI
from dotenv import load_dotenv

import os

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.aitunnel.ru/v1"
)

MODEL = os.getenv("MODEL", "gpt-4o-mini")

async def ask_ai(prompt):
    res = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return res.choices[0].message.content

async def detect_intent(text):
    prompt = f"""
    Определи намерение пользователя.

    Варианты:
    PODBOR (подбор авто)
    COMPARE (сравнение авто)
    BUY (стоит ли брать)
    OTHER

    Ответь ТОЛЬКО одним словом.

    Запрос: {text}
    """

    res = await ask_ai(prompt)
    return res.strip().upper()


async def car_podbor(text):
    return await ask_ai(f"""
    Подбери авто: {text}

    3-5 вариантов
    плюсы/минусы
    цена

    Коротко, Telegram стиль
    """)


async def compare_cars(text):
    return await ask_ai(f"""
    Сравни: {text}

    мощность / расход / надежность
    итог
    """)


async def should_buy(text):
    return await ask_ai(f"""
    Стоит ли брать: {text}

    плюсы
    минусы
    проблемы
    вердикт
    """)

async def is_auto_question_ai(text):
    prompt = f"""
    Это вопрос про автомобили?

    Ответь строго:
    YES или NO

    Вопрос: {text}
    """

    res = await ask_ai(prompt)

    return "YES" in res.upper()