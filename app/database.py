"""
Database ulanish va session boshqaruvi.
Async SQLAlchemy + PostgreSQL (asyncpg driver).
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import config


class Base(DeclarativeBase):
    """Barcha modellar uchun asosiy class."""
    pass


# Async engine - bazaga ulanish
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,          # SQL so'rovlarni terminalga chiqarmaslik (production uchun)
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # uzilgan ulanishlarni avtomatik tekshirish
)

# Session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager - har bir so'rov uchun yangi session ochadi
    va oxirida avtomatik yopadi.

    Foydalanish:
        async with get_session() as session:
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Barcha jadvallarni (modellarni) bazada yaratadi.
    Loyiha birinchi marta ishga tushganda chaqiriladi.
    """
    # Modellarni import qilish - Base.metadata ga ro'yxatdan o'tishi uchun
    from app.models import (  # noqa: F401
        branch, admin, user, table, category, product,
        cart, order, order_item, payment, favorite,
        rating, promo, reservation,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Bot to'xtaganda bazaga ulanishni yopish."""
    await engine.dispose()
