# bot/handlers/crypto.py
import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

API_URL = "http://localhost:8000"  # при деплое вынеси в .env

router = Router(name="crypto_inline_ru")

# Алгоритмы, требующие «ключ»
ALGORITHMS_REQUIRE_KEY = {"Цезарь"}

# ================== Состояния FSM ==================
class CryptoState(StatesGroup):
    action = State()          # encrypt | decrypt | hash
    algorithm = State()       # Цезарь | RSA | SHA256
    waiting_text = State()
    waiting_key = State()
    menu_msg_id = State()     # id сообщения с меню (чтобы редактировать)

# ================== Клавиатуры ==================
def algorithms_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Цезарь", callback_data="crypto:algo:Цезарь"),
         InlineKeyboardButton(text="RSA", callback_data="crypto:algo:RSA")],
        [InlineKeyboardButton(text="SHA256", callback_data="crypto:algo:SHA256")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="crypto:cancel")],
    ])

def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="crypto:cancel")]
    ])

# ================== ОТМЕНА (inline + текст) ==================
@router.callback_query(F.data == "crypto:cancel")
async def on_cancel_cb(q: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    menu_id = data.get("menu_msg_id")
    await state.clear()
    try:
        if menu_id:
            await q.message.edit_text("❌ Отменено.", reply_markup=None)
        else:
            await q.message.answer("❌ Отменено.")
    except Exception:
        await q.message.answer("❌ Отменено.")
    await q.answer()

@router.message(F.text.casefold() == "отмена")
async def on_cancel_text(message: Message, state: FSMContext):
    data = await state.get_data()
    menu_id = data.get("menu_msg_id")
    await state.clear()
    if menu_id:
        try:
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=menu_id, text="❌ Отменено.")
        except Exception:
            pass
    await message.answer("❌ Отменено.")

# ================== Точки входа ==================
@router.message(F.text == "🔐 Шифрование")
async def start_encrypt(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(action="encrypt")
    msg = await message.answer("🔐 Выберите алгоритм:", reply_markup=algorithms_kb())
    await state.update_data(menu_msg_id=msg.message_id)
    await state.set_state(CryptoState.action)

@router.message(F.text == "🔓 Дешифрование")
async def start_decrypt(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(action="decrypt")
    msg = await message.answer("🔓 Выберите алгоритм:", reply_markup=algorithms_kb())
    await state.update_data(menu_msg_id=msg.message_id)
    await state.set_state(CryptoState.action)


# ================== Выбор алгоритма (inline) ==================
@router.callback_query(F.data.startswith("crypto:algo:"))
async def choose_algorithm(q: CallbackQuery, state: FSMContext):
    algo = q.data.split("crypto:algo:", 1)[1]
    await state.update_data(algorithm=algo)
    try:
        await q.message.edit_text(f"Алгоритм: {algo}\n\n✍️ Отправьте текст для обработки.", reply_markup=cancel_kb())
    except Exception:
        await q.message.answer(f"Алгоритм: {algo}\n\n✍️ Отправьте текст для обработки.", reply_markup=cancel_kb())
    await state.set_state(CryptoState.waiting_text)
    await q.answer()

# ================== Приём текста ==================
@router.message(CryptoState.waiting_text, F.text.len() > 0)
async def receive_text(message: Message, state: FSMContext):
    data = await state.get_data()
    algo = data.get("algorithm")
    action = data.get("action")
    text = message.text

    await state.update_data(text=text)

    if algo in ALGORITHMS_REQUIRE_KEY and action in {"encrypt", "decrypt"}:
        await state.set_state(CryptoState.waiting_key)
        await message.answer("🔑 Введите ключ (целое число, можно отрицательное):", reply_markup=cancel_kb())
        return

    # RSA и SHA256 — сразу в API
    await call_api_and_reply(message, action, algo, text, params=None)
    await state.clear()

# ================== Приём ключа (для Цезаря) ==================
@router.message(CryptoState.waiting_key)
async def receive_key(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        key = int(raw)
        if not -10_000 <= key <= 10_000:
            raise ValueError
    except Exception:
        await message.answer("Ключ должен быть целым числом в диапазоне −10000…10000. Введите заново:", reply_markup=cancel_kb())
        return

    data = await state.get_data()
    algo = data.get("algorithm")
    action = data.get("action")
    text = data.get("text", "")

    await call_api_and_reply(message, action, algo, text, params={"key": key})
    await state.clear()

# ================== Вызов API и ответ ==================
async def call_api_and_reply(message: Message, action: str, algo: str, text: str, params: dict | None):
    try:
        payload = {"algorithm": algo, "text": text}
        if params:
            payload["params"] = params

        resp = requests.post(f"{API_URL}/crypto/{action}", json=payload, timeout=20)

        if resp.status_code == 200:
            result = resp.json().get("result")
            header = {"encrypt": "Зашифрованный", "decrypt": "Расшифрованный", "hash": "Хэш"}.get(action, "Результат")
            extra = ""
            if params and "key" in params:
                extra = f"▫️ Ключ: {params['key']}\n"

            await message.answer(
                f"▫️ Алгоритм: {algo}\n▫️ Режим: {'Шифрование' if action=='encrypt' else 'Дешифрование' if action=='decrypt' else 'Хэширование'}\n"
                f"{extra}\n<b>{header}:</b>\n<code>{result}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"⚠️ Ошибка API: {resp.status_code}\n{resp.text}")
    except Exception as e:
        await message.answer(f"❌ Не удалось выполнить операцию:\n{e}")

# ================== Фолбек вне сценариев ==================
@router.message(F.text)
async def fallback(message: Message, state: FSMContext):
    if await state.get_state():
        return
    await message.answer("Выберите режим и алгоритм:", reply_markup=algorithms_kb())
