from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.db import get_db
from api import models
from datetime import datetime

# ==========================
# ШАПКА (инициализация БД)
# ==========================
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # 👈 обязательно
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

models.Base.metadata.create_all(bind=engine)   # 👈 создаём ВСЕ таблицы

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ==========================
# СИДИРУЕМ ПОЛЬЗОВАТЕЛЕЙ (для /documents)
# ==========================
def seed_users():
    db = TestingSessionLocal()
    bot_user = models.BotUser(
        id=1,
        telegram_id=111111111,
        username="tester",
        joined_at=datetime.utcnow()
    )
    desktop_user = models.DesktopUser(
        id=1,
        device_name="TestPC",
        bot_user_id=1,
        created_at=datetime.utcnow()
    )
    db.add(bot_user)
    db.add(desktop_user)
    db.commit()
    db.close()

seed_users()   # 👈 один раз перед тестами


# ==========================
# 🧪 Вот ЭТО и есть тест
# ==========================
def test_documents_crud_flow():
    payload = {
        "filename": "demo.cvc",
        "encrypted_data": "48656c6c6f2c20576f726c6421",  # HEX "Hello, World!"
        "cipher_meta": {"method": "demo-aes"}
    }

    # 1) Upload
    r = client.post("/documents/upload", json=payload)
    assert r.status_code == 200
    doc = r.json()
    doc_id = doc["id"]

    # 2) List
    r = client.get("/documents/list")
    assert r.status_code == 200
    assert any(d["id"] == doc_id for d in r.json())

    # 3) Get
    r = client.get(f"/documents/{doc_id}")
    assert r.status_code == 200
    assert r.json()["encrypted_data"] == payload["encrypted_data"]

    # 4) Delete
    r = client.delete(f"/documents/{doc_id}")
    assert r.status_code == 200

    # 5) Проверяем что реально удалён
    r = client.get(f"/documents/{doc_id}")
    assert r.status_code == 404
