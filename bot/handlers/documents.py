import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile

API_URL = "http://localhost:8000"
router = Router()


@router.message(F.text == "📂 Мои документы")
async def my_documents(message: Message):
    telegram_id = message.from_user.id
    try:
        resp = requests.get(f"{API_URL}/documents/list", params={"telegram_id": telegram_id})
        if resp.status_code == 200:
            docs = resp.json()
            if not docs:
                await message.answer("📂 У вас пока нет документов.")
                return
            for d in docs:
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="📥 Скачать", callback_data=f"get:{d['id']}"),
                            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del:{d['id']}")
                        ]
                    ]
                )
                text = f"🆔 {d['id']} | {d['filename']} | {d['created_at']}"
                await message.answer(text, reply_markup=kb)
        else:
            await message.answer(f"⚠️ Ошибка API: {resp.text}")
    except Exception as e:
        await message.answer(f"❌ Не удалось подключиться к API:\n{e}")


@router.callback_query(F.data.startswith("get:"))
async def get_document(call: CallbackQuery):
    doc_id = int(call.data.split(":")[1])
    try:
        resp = requests.get(f"{API_URL}/documents/{doc_id}")
        if resp.status_code == 200:
            doc = resp.json()
            if "encrypted_data" not in doc:
                await call.message.answer("⚠️ API не вернул содержимое документа.")
                return
            filename = doc["filename"]
            encrypted_data = bytes.fromhex(doc["encrypted_data"])
            await call.message.answer_document(
                document=BufferedInputFile(encrypted_data, filename=filename),
                caption=f"📂 {filename}"
            )
        else:
            await call.message.answer(f"⚠️ Ошибка API: {resp.text}")
    except Exception as e:
        await call.message.answer(f"❌ Не удалось скачать документ:\n{e}")
    await call.answer()  # закрыть "часики"


@router.callback_query(F.data.startswith("del:"))
async def delete_document(call: CallbackQuery):
    doc_id = int(call.data.split(":")[1])
    try:
        resp = requests.delete(f"{API_URL}/documents/{doc_id}")
        if resp.status_code == 200:
            await call.message.answer(f"🗑 Документ {doc_id} удалён.")
        else:
            await call.message.answer(f"⚠️ Ошибка API: {resp.text}")
    except Exception as e:
        await call.message.answer(f"❌ Не удалось удалить документ:\n{e}")
    await call.answer()
