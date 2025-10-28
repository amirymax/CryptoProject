from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.db import get_db
from api import models

# ==========================
# ИНИЦИАЛИЗАЦИЯ IN-MEMORY БД
# ==========================
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ВАЖНО: создаём все таблицы после импорта models
models.Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def seed_bot_user(telegram_id: int = 222222222, username: str = "link_tester") -> int:
    """Создаём BotUser и возвращаем его id."""
    db = TestingSessionLocal()
    bot_user = models.BotUser(
        telegram_id=telegram_id,
        username=username,
        joined_at=datetime.utcnow()
    )
    db.add(bot_user)
    db.commit()
    db.refresh(bot_user)
    db.close()
    return bot_user.id


def get_db_rows(model):
    """Утилита для отладки — вернуть все строки конкретной таблицы (не используется в ассёртах)."""
    db = TestingSessionLocal()
    rows = db.query(model).all()
    db.close()
    return rows


# ==========================
# 🧪 СКВОЗНОЙ ТЕСТ ПРИВЯЗКИ ПК
# ==========================
def test_link_generate_and_verify_flow():
    # 1) Подготовка: есть зарегистрированный BotUser
    bot_user_id = seed_bot_user(telegram_id=999000111, username="alice")

    # 2) Генерируем одноразовый код по telegram_id
    r = client.post("/link/generate", json={"telegram_id": 999000111})
    assert r.status_code == 200, r.text
    payload = r.json()
    assert "code" in payload and payload["code"].isdigit() and len(payload["code"]) == 4
    code = payload["code"]

    # 3) Верифицируем на Desktop (device_name) — создаётся/обновляется DesktopUser, код удаляется
    r = client.post("/link/verify", json={"device_name": "TestPC-LinkFlow", "code": code})
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "ok"

    # 4) Проверяем в БД:
    db = TestingSessionLocal()

    # 4.1) DesktopUser создан и привязан к верному bot_user_id
    du = db.query(models.DesktopUser).filter(models.DesktopUser.device_name == "TestPC-LinkFlow").first()
    assert du is not None, "DesktopUser должен быть создан после verify"
    assert du.bot_user_id == bot_user_id, "DesktopUser.bot_user_id должен соответствовать BotUser.id"

    # 4.2) LinkCode одноразовый — должен быть удалён
    lc = db.query(models.LinkCode).filter(models.LinkCode.code == code).first()
    assert lc is None, "LinkCode должен удаляться после успешной привязки"

    db.close()
