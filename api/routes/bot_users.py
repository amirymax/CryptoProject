from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..db import get_db

router = APIRouter(prefix="/bot_users", tags=["bot_users"])


@router.post("/register")
def register_bot_user(user: schemas.BotUserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_bot_user_by_tg(db, user.telegram_id)
    if db_user:
        return {"status": "exists", "id": db_user.id}
    new_user = crud.create_bot_user(db, user)
    return {"status": "created", "id": new_user.id}
