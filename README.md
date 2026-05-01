# Talpis Bot

Telegram бот для уведомлений об изменениях в календаре мероприятий Talpis.

## Функции
- Уведомления о новых мероприятиях, изменениях и отменах
- ИИ-ответы на вопросы о расписании (через Mistral)
- Рассылка в группу и личку подписчиков

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `MISTRAL_API_KEY` | API ключ Mistral |
| `GROUP_CHAT_ID` | ID группы/канала (со знаком минус, напр. `-1001234567890`) |
| `SPREADSHEET_ID` | ID Google таблицы |
| `SHEET_GID` | GID листа "api" в таблице |
| `CHECK_INTERVAL_MINUTES` | Интервал проверки изменений (default: 30) |

## Деплой на Railway

1. Залей на GitHub
2. В Railway → New Project → Deploy from GitHub
3. Добавь переменные окружения
4. Railway автоматически запустит через Procfile

## Как узнать GROUP_CHAT_ID

1. Добавь бота в группу
2. Напиши в группе любое сообщение
3. Открой: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Найди `"chat":{"id":...}` — это и есть GROUP_CHAT_ID

## Структура

```
bot.py          — точка входа
config.py       — конфиг из env
sheets.py       — чтение Google Sheets
comparator.py   — сравнение снимков и форматирование изменений
scheduler.py    — планировщик проверок и рассылка
ai_handler.py   — ИИ ответы через Mistral
handlers.py     — Telegram хендлеры
```
