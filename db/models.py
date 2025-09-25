from sqlalchemy import Column, Integer, BigInteger, String, TIMESTAMP, ForeignKey, JSON, LargeBinary, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BotUser(Base):
    __tablename__ = "bot_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    joined_at = Column(TIMESTAMP, server_default=func.now())

    desktop_user = relationship("DesktopUser", back_populates="bot_user", uselist=False)
    codes = relationship("LinkCode", back_populates="bot_user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="bot_user", cascade="all, delete-orphan")


class DesktopUser(Base):
    __tablename__ = "desktop_users"

    id = Column(Integer, primary_key=True, index=True)
    bot_user_id = Column(Integer, ForeignKey("bot_users.id", ondelete="CASCADE"))
    device_name = Column(String, nullable=False)   # 👈 новое поле
    created_at = Column(TIMESTAMP, server_default=func.now())

    bot_user = relationship("BotUser", back_populates="desktop_user")
    documents = relationship("Document", back_populates="desktop_user", cascade="all, delete-orphan")


class LinkCode(Base):
    __tablename__ = "link_codes"

    id = Column(Integer, primary_key=True, index=True)
    bot_user_id = Column(Integer, ForeignKey("bot_users.id", ondelete="CASCADE"))
    code = Column(String(10), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)

    bot_user = relationship("BotUser", back_populates="codes")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    bot_user_id = Column(Integer, ForeignKey("bot_users.id", ondelete="CASCADE"))
    desktop_user_id = Column(Integer, ForeignKey("desktop_users.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    cipher_meta = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    bot_user = relationship("BotUser", back_populates="documents")
    desktop_user = relationship("DesktopUser", back_populates="documents")
