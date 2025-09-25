from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


# --- Bot Users ---
def create_bot_user(db: Session, user: schemas.BotUserCreate):
    db_user = models.BotUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_bot_user_by_tg(db: Session, telegram_id: int):
    return db.query(models.BotUser).filter(models.BotUser.telegram_id == telegram_id).first()


# --- Desktop Users ---
def create_desktop_user(db: Session, desktop: schemas.DesktopUserCreate):
    db_desktop = models.DesktopUser(**desktop.dict())
    db.add(db_desktop)
    db.commit()
    db.refresh(db_desktop)
    return db_desktop


# --- Link Codes ---
def verify_code(db: Session, code: str):
    db_code = db.query(models.LinkCode).filter(models.LinkCode.code == code).first()
    if db_code and db_code.expires_at > datetime.utcnow():
        return db_code
    return None


# --- Documents ---
def create_document(db: Session, doc: schemas.DocumentCreate, bot_user_id: int, desktop_user_id: int):
    db_doc = models.Document(
        filename=doc.filename,
        encrypted_data=doc.encrypted_data,
        cipher_meta=doc.cipher_meta,
        bot_user_id=bot_user_id,
        desktop_user_id=desktop_user_id,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def get_documents(db: Session, bot_user_id: int):
    return db.query(models.Document).filter(models.Document.bot_user_id == bot_user_id).all()
