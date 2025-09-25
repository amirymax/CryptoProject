import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден в .env")

# Создаём движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Сессия для работы с БД
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Базовый класс моделей
Base = declarative_base()


# Dependency для FastAPI (будем использовать в эндпоинтах)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
