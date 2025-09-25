import requests
from aiogram import Router, types
from aiogram.types import Message
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

router = Router()


@router.message(lambda m: m.text == "🔑 Привязать компьютер")
async def link_computer(message: Message):
    """Генерация одноразового кода и отправка пользователю"""
    telegram_id = message.from_user.id

    try:
        # Запрос к API для генерации кода
        resp = requests.post(
            f"{API_URL}/link/generate",
            json={"telegram_id": telegram_id}
        )
        if resp.status_code == 200:
            data = resp.json()
            code = data["code"]
            expires = data["expires_at"]
            await message.answer(
                f"🔑 Ваш код для привязки: <b>{code}</b>\n"
                f"⏳ Действителен до: {expires}",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"⚠️ Ошибка API: {resp.text}")
    except Exception as e:
        await message.answer(f"❌ Не удалось подключиться к API:\n{e}")
