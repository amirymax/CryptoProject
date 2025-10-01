from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- BotUser ---
class BotUserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None


class BotUserCreate(BotUserBase):
    pass


class BotUser(BotUserBase):
    id: int
    joined_at: datetime

    class Config:
        orm_mode = True


# --- DesktopUser ---
class DesktopUserBase(BaseModel):
    device_name: str


class DesktopUserCreate(DesktopUserBase):
    bot_user_id: int


class DesktopUser(DesktopUserBase):
    id: int
    bot_user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --- Documents ---
class DocumentBase(BaseModel):
    filename: str
    cipher_meta: Optional[dict] = None


class DocumentCreate(DocumentBase):
    encrypted_data: bytes


class Document(DocumentBase):
    id: int
    created_at: datetime
    encrypted_data: str   

    class Config:
        orm_mode = True

class LinkVerify(BaseModel):
    device_name: str
    code: str
