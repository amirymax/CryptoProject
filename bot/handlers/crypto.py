import requests
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

API_URL = "http://localhost:8000"

router = Router()


# --- FSM состояния ---
class CryptoState(StatesGroup):
    waiting_for_algorithm = State()
    waiting_for_text = State()
    waiting_for_action = State()  # encrypt / decrypt / hash


# --- Главное меню для выбора алгоритма ---
def algorithms_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Цезарь"), KeyboardButton(text="RSA")],
        [KeyboardButton(text="Эль-Гамаль"), KeyboardButton(text="SHA256")],
        [KeyboardButton(text="Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# --- Шифрование ---
@router.message(F.text == "🔐 Шифрование")
async def choose_algorithm_encrypt(message: Message, state: FSMContext):
    await state.set_state(CryptoState.waiting_for_algorithm)
    await state.update_data(action="encrypt")
    await message.answer("🔐 Выберите алгоритм:", reply_markup=algorithms_menu())


# --- Дешифрование ---
@router.message(F.text == "🔓 Дешифрование")
async def choose_algorithm_decrypt(message: Message, state: FSMContext):
    await state.set_state(CryptoState.waiting_for_algorithm)
    await state.update_data(action="decrypt")
    await message.answer("🔓 Выберите алгоритм:", reply_markup=algorithms_menu())


# --- Хэширование ---
@router.message(F.text == "📝 Хэширование")
async def choose_algorithm_hash(message: Message, state: FSMContext):
    await state.set_state(CryptoState.waiting_for_algorithm)
    await state.update_data(action="hash")
    await message.answer("📝 Выберите алгоритм хэширования:", reply_markup=algorithms_menu())


# --- Получаем выбор алгоритма ---
@router.message(CryptoState.waiting_for_algorithm)
async def set_algorithm(message: Message, state: FSMContext):
    algo = message.text
    if algo == "Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=None)
        return

    await state.update_data(algorithm=algo)
    await state.set_state(CryptoState.waiting_for_text)
    await message.answer(f"✍️ Введите текст для {algo}:")


# --- Получаем текст и отправляем на API ---
@router.message(CryptoState.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    data = await state.get_data()
    algo = data.get("algorithm")
    action = data.get("action")
    text = message.text

    try:
        resp = requests.post(
            f"{API_URL}/crypto/{action}",
            json={"algorithm": algo, "text": text}
        )
        if resp.status_code == 200:
            result = resp.json().get("result")
            await message.answer(f"✅ Результат ({algo}, {action}):\n\n<code>{result}</code>", parse_mode="HTML")
        else:
            await message.answer(f"⚠️ Ошибка API: {resp.text}")
    except Exception as e:
        await message.answer(f"❌ Не удалось выполнить операцию:\n{e}")

    await state.clear()
