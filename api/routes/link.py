from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from .. import crud, models, schemas
from ..db import get_db

router = APIRouter(prefix="/link", tags=["link"])


@router.post("/generate")
def generate_link_code(data: dict, db: Session = Depends(get_db)):
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="telegram_id required")

    bot_user = db.query(models.BotUser).filter(models.BotUser.telegram_id == telegram_id).first()
    if not bot_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерация кода
    code = str(random.randint(1000, 9999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    link_code = models.LinkCode(
        bot_user_id=bot_user.id,
        code=code,
        expires_at=expires_at
    )
    db.add(link_code)
    db.commit()
    db.refresh(link_code)

    return {"code": code, "expires_at": expires_at.isoformat()}

@router.post("/verify")
def verify_link(data: schemas.LinkVerify, database: Session = Depends(get_db)):
    """
    Проверка кода из Telegram и привязка к DesktopUser
    """
    # Проверяем наличие кода
    link_code = (
        database.query(models.LinkCode)
        .filter(models.LinkCode.code == data.code)
        .first()
    )
    if not link_code:
        raise HTTPException(status_code=404, detail="Not Found")

    # Проверяем, есть ли уже DesktopUser с таким device_name
    desktop_user = (
        database.query(models.DesktopUser)
        .filter(models.DesktopUser.device_name == data.device_name)
        .first()
    )

    if desktop_user:
        # Обновляем user_id (если вдруг был другой)
        desktop_user.user_id = link_code.user_id
    else:
        # Создаём нового desktop_user
        desktop_user = models.DesktopUser(
            device_name=data.device_name, bot_user_id=link_code.bot_user_id
        )
        database.add(desktop_user)

    # Удаляем использованный код (одноразовый)
    database.delete(link_code)
    database.commit()

    return {"status": "ok", "message": "Успешная привязка"}