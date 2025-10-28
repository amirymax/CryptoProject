# CryptoProject — CryptoDesk + CryptoBot + API

Учебный проект для предмета «Математические основы криптологии».

## Состав
- **API (FastAPI)** — `api/`
- **Telegram-бот (aiogram 3.x)** — `bot/`
- **Десктоп (PySide6)** — `cryptodesk/`
- **Ядро шифрования** — `crypto_core/`
- **Тесты (pytest)** — `tests/`

---

## 1) Быстрый старт

### 1.1 Установка
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate

pip install -U pip
pip install -r requirements.txt
