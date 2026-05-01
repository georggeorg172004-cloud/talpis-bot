import logging
from datetime import date

import aiohttp

import config
from sheets import fetch_events, events_to_text

logger = logging.getLogger(__name__)

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


async def ask_ai(question: str) -> str:
    try:
        events = await fetch_events()
        schedule = events_to_text(events)
    except Exception as e:
        logger.error(f"Failed to fetch events for AI: {e}")
        return "Не удалось загрузить расписание. Попробуй позже."

    today = date.today().isoformat()

    system_prompt = f"""Ты помощник по расписанию мероприятий компании Talpis.
Сегодня: {today}

{schedule}

Отвечай кратко и по делу на русском языке.
Если мероприятие не найдено — так и скажи.
Для дат используй формат ДД.ММ.ГГГГ.
Если спрашивают про "ближайшее" — найди следующее после сегодняшней даты.
"""

    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "max_tokens": 500,
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {config.MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(MISTRAL_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"Mistral error {resp.status}: {text}")
                return "Ошибка при обращении к ИИ. Попробуй позже."
            data = await resp.json()

    return data["choices"][0]["message"]["content"].strip()
