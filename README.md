# DeCrypto

Полноценная инструкция для тех, кто хочет **клонировать** проект и **запустить локально вручную** (без Docker). README рассчитан на Windows 10/11 и Linux (Ubuntu/Debian). Для macOS шаги аналогичны Linux.

---

## 1) Краткое описание

- **CryptoDesk (PySide6)** — десктоп‑приложение: шифрование/дешифрование, хэширование, подписи, загрузка зашифрованных файлов в БД.
- **CryptoBot (aiogram 3)** — Telegram‑бот: регистрация, привязка ПК, список документов, скачивание/удаление, шифрование/дешифрование/хэширование через API.
- **API (FastAPI)** — связующее звено между ботом, десктопом и базой.
- **PostgreSQL** — хранит пользователей, коды привязки и документы (HEX + метаданные).

---

## 2) Стек и версии

- Python **3.10+**
- FastAPI, Pydantic v2
- SQLAlchemy, psycopg2‑binary (для PostgreSQL)
- aiogram **3.18**
- PySide6 (GUI)
- cryptography (RSA, подписи), hashlib (SHA‑256)
- requests (клиент для бота/десктопа)
- pytest, httpx (для тестов)

> Все зависимости указаны в `requirements.txt`.

---

## 3) Структура репозитория

```
CRYPTOPROJECT/
│── api/             # FastAPI (сервер)
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── routes/
│       ├── __init__.py
│       ├── link.py
│       ├── documents.py
│       └── crypto.py
│
│── bot/             # Telegram-бот (aiogram 3.x)
│   ├── main.py      # /start и меню
│   └── handlers/
│       ├── __init__.py
│       ├── link.py
│       ├── documents.py
│       └── crypto.py
│
│── cryptodesk/      # Десктопное приложение (PySide6)
│   ├── main.py
│   └── tabs/
│       ├── caesar_tab.py
│       ├── link_tab.py
│       ├── docs_tab.py
│       ├── freq_tab.py
│       ├── hash_tab.py
│       ├── primes_tab.py
│       ├── classic_tab.py
│       └── ...
│
│── crypto_core/     # Алгоритмы
│   ├── classic/
│   ├── asymmetric/
│   ├── hashing.py
│   └── primes.py
│
│── db/              # Работа с БД
│   ├── models.py
│   ├── init_db.py
│   ├── check_db.py
│   └── migrations (опц.)
│
│── tests/
│── .env
│── requirements.txt
│── docker-compose.yml (опц.)
│── README.md
```

---

## 4) Предварительные требования

1. Установите **Python 3.10+**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Установите **PostgreSQL 14+**: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
3. Создайте виртуальное окружение и установите зависимости:

```bash
# Windows (PowerShell)
python -m venv env
./env/Scripts/activate
pip install -r requirements.txt

# Linux/macOS
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

> Если при установке зависимостей появится ошибка по `psycopg2`, используйте колесо `psycopg2-binary` (оно уже в requirements).

---

## 5) Настройка PostgreSQL

1. **Создайте БД и пользователя** (выполните в psql под `postgres`):

```sql
CREATE DATABASE crypto;
CREATE USER crypto_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE crypto TO crypto_user;
```

2. **Разрешите подключение** (обычно по умолчанию): проверьте `pg_hba.conf` и `postgresql.conf`, перезапустите службу при необходимости.

3. **Инициализация таблиц**: из корня проекта запустите `db/init_db.py` (создаёт таблицы через SQLAlchemy):

```bash
# при активном venv
python db/init_db.py
```

4. **Проверка соединения**:

```bash
python db/check_db.py
```

Если видите успешный вывод — база готова.

---

## 6) Конфигурация (.env)

Создайте файл **.env** в корне проекта. Пример:

```dotenv
# === API ===
API_HOST=127.0.0.1
API_PORT=8000
DATABASE_URL=postgresql+psycopg2://crypto_user:strong_password@127.0.0.1:5432/crypto

# === BOT ===
BOT_TOKEN=1234567890:AA...your_token...
API_BASE=http://127.0.0.1:8000

# === DESKTOP ===
API_URL=http://127.0.0.1:8000

# Опц.: логирование
LOG_LEVEL=INFO
```

- `DATABASE_URL` — строка подключения SQLAlchemy.
- `API_BASE`/`API_URL` — адрес API, который будет использовать бот/десктоп.
- `BOT_TOKEN` — токен Telegram‑бота от BotFather.

> Если запускаете сервер и клиент на разных машинах — замените `127.0.0.1` на IP сервера.

---

## 7) Запуск

### 7.1) Запуск API (FastAPI)

```bash
# из корня проекта, при активном venv
uvicorn api.main:app --host %API_HOST% --port %API_PORT% --reload   # Windows
# или
uvicorn api.main:app --host $API_HOST --port $API_PORT --reload     # Linux/macOS
```

Проверка: откройте в браузере [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — должна открыться Swagger‑документация.

### 7.2) Запуск Telegram‑бота

```bash
python bot/main.py
```

Бот подключится к API по адресу `API_BASE` из .env. В Telegram отправьте `/start`.

### 7.3) Запуск десктопа (CryptoDesk)

```bash
python cryptodesk/main.py
```

Приложение стартует в тёмной теме, с вкладками («Шифр Цезаря», «Документы в БД», и др.).

---

## 8) Быстрый сценарий проверки (end‑to‑end)

1. В боте: `/start` → **«🔑 Привязать компьютер»** → получите код.
2. В CryptoDesk: вкладка **«Привязка к Telegram»** → введите имя устройства и код → «Привязать» → «Успешная привязка».
3. В CryptoDesk: вкладка **«Документы в БД»** → «📂 Загрузить документ в БД» (любая картинка/текст) → «📋 Показать список».
4. В боте: **«📂 Мои документы»** → увидите свой файл → **скачать** или **удалить**.
5. В боте: **«🔐 Шифрование → Цезарь»** → текст → ключ → получите зашифрованный текст.
6. В боте: **«🔐 Шифрование → RSA»** → текст → получите base64‑строку (может быть из нескольких частей через `;`).
7. В боте: **«🔓 Дешифрование → RSA»** → вставьте шифртекст → получите исходный текст.

---

## 9) Тесты

Установите dev-зависимости (если выделены) и запустите:

```bash
pytest -q
```

Если увидите ошибку вида `The starlette.testclient module requires the httpx package to be installed` — добавьте `httpx` (есть в requirements) и повторите.

---

## 10) Частые ошибки и решения

### 10.1) `psql: FATAL: Peer authentication failed for user "postgres"`

- Используйте логин/пароль пользователя БД (например, `crypto_user`).
- В `pg_hba.conf` замените `peer` на `md5` для локальных подключений и перезапустите PostgreSQL.

### 10.2) Служба PostgreSQL «active (exited)»

- Это мета‑сервис. Проверьте конкретный инстанс (`postgresql@14-main` и т.п.).
- Убедитесь, что порт `5432` слушается (`ss -ltnp | grep 5432`).

### 10.3) API отвечает 422 на `/documents/list`

- Эндпоинт ожидает параметры/контекст пользователя. Проверьте актуальный `api/routes/documents.py` и привязку bot\_user.

### 10.4) «API не вернул содержимое документа»

- Удостоверьтесь, что поле `encrypted_data` включено в `schemas.Document` и сериализуется как HEX.
- Проверьте `GET /documents/{id}`: объект должен включать `filename`, `encrypted_data`.

### 10.5) Бот не реагирует на «Отмена»

- Убедитесь, что подключена актуальная версия `bot/handlers/crypto.py` с **inline‑кнопками** и глобальным хендлером отмены.

### 10.6) RSA возвращает «not implemented»

- Замените `api/routes/crypto.py` на версию, использующую `crypto_core.asymmetric.rsa` и перезапустите API.

---

## 11) Переменные окружения по модулям

### API

- `DATABASE_URL` — строка подключения SQLAlchemy (PostgreSQL).
- `API_HOST`, `API_PORT` — адрес и порт запуска.

### BOT

- `BOT_TOKEN` — токен бота от BotFather.
- `API_BASE` — базовый адрес API.

### DESKTOP

- `API_URL` — базовый адрес API.

---

## 12) Безопасность

- Коды привязки действуют ограниченное время (по умолчанию 10 минут).
- Документы хранятся в БД только в **зашифрованном виде** (HEX + метаданные).
- Для RSA используется схема **OAEP(SHA‑256)**, для подписей — **PSS(SHA‑256)**.
- Не храните приватные ключи в репозитории. Для проверки можно пользоваться демо‑парой (глобальная пара создаётся в рантайме).

---

## 13) Дорожная карта (опционально)

- Эль‑Гамаль в API и боте (params для ключей).
- Веб‑панель статистики (FastAPI + шаблоны или отдельный frontend).
- Докеризация (API + Postgres + Bot) и CI.
- Больше юнит‑тестов для crypto\_core и API.

---

## 14) Лицензия

Учебный проект. Условия распространения/использования — по договорённости с автором.

---

## 15) Контакты

Автор: **Зикрулло Амири**\
Проект: De*Crypto*\
Вопросы по запуску и доработкам — через Issues или личные сообщения.

