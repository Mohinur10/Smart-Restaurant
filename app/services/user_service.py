"""Foydalanuvchi (User) bilan bog'liq operatsiyalar."""
from sqlalchemy import select

from app.database import get_session
from app.models import User


async def get_or_create_user(telegram_id: int, full_name: str | None, username: str | None) -> User:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            # Ma'lumotlarni yangilab turamiz
            updated = False
            if user.full_name != full_name:
                user.full_name = full_name
                updated = True
            if user.username != username:
                user.username = username
                updated = True
            if updated:
                await session.commit()
            return user

        user = User(telegram_id=telegram_id, full_name=full_name, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user_by_id(user_id: int) -> User | None:
    async with get_session() as session:
        return await session.get(User, user_id)


async def set_user_phone(user_id: int, phone: str) -> None:
    async with get_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.phone = phone
            await session.commit()


async def add_bonus(user_id: int, amount: float) -> None:
    """Bonus tizimi: foydalanuvchi balansiga bonus qo'shish."""
    async with get_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.bonus_balance = float(user.bonus_balance) + amount
            await session.commit()
