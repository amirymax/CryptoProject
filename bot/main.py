import asyncio
import os
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from bot.handlers import link

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://localhost:8000"  # адрес нашего FastAPI

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Главное меню ---
def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🔑 Привязать компьютер")],
        [KeyboardButton(text="📂 Мои документы")],
        [KeyboardButton(text="🔐 Шифрование"), KeyboardButton(text="🔓 Дешифрование")],
        [KeyboardButton(text="📝 Хэширование")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# --- /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Регистрация пользователя в API"""
    telegram_id = message.from_user.id
    username = message.from_user.username

    try:
        resp = requests.post(
            f"{API_URL}/bot_users/register",
            json={"telegram_id": telegram_id, "username": username}
        )
        if resp.status_code == 200:
            await message.answer("✅ Вы успешно зарегистрированы!", reply_markup=main_menu())
        else:
            await message.answer(f"⚠️ Ошибка при регистрации: {resp.text}")
    except Exception as e:
        await message.answer(f"❌ Не удалось подключиться к API:\n{e}")

dp.include_router(link.router)
# --- Запуск ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
