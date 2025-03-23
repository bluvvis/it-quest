from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, BigInteger, String, DateTime
from datetime import datetime

from bot.config import DB_URL

engine: AsyncEngine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String)
    first_connection = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    current_state = Column(String)  # Здесь можно хранить строковое название этапа
    subscription_status = Column(String)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"
