"""Saqlangan (Favorite) mahsulotlar bilan ishlash."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Favorite


async def is_favorite(user_id: int, product_id: int) -> bool:
    async with get_session() as session:
        result = await session.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        return result.scalar_one_or_none() is not None


async def toggle_favorite(user_id: int, product_id: int) -> bool:
    """True - qo'shildi, False - olib tashlandi."""
    async with get_session() as session:
        result = await session.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        fav = result.scalar_one_or_none()
        if fav:
            await session.delete(fav)
            await session.commit()
            return False
        session.add(Favorite(user_id=user_id, product_id=product_id))
        await session.commit()
        return True


async def get_user_favorites(user_id: int) -> list[Favorite]:
    async with get_session() as session:
        result = await session.execute(
            select(Favorite).options(selectinload(Favorite.product)).where(Favorite.user_id == user_id)
        )
        return list(result.scalars().all())
