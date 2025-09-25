import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from db.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("✅ Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
