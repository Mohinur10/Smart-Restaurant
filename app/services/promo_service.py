"""Promokod (PromoCode) CRUD."""
from sqlalchemy import select

from app.database import get_session
from app.models import PromoCode


async def get_promo_by_code(code: str) -> PromoCode | None:
    async with get_session() as session:
        result = await session.execute(select(PromoCode).where(PromoCode.code == code.upper()))
        return result.scalar_one_or_none()


async def create_promo(code: str, discount_percent: int, usage_limit: int | None = None) -> PromoCode:
    async with get_session() as session:
        promo = PromoCode(code=code.upper(), discount_percent=discount_percent, usage_limit=usage_limit)
        session.add(promo)
        await session.commit()
        await session.refresh(promo)
        return promo


async def get_all_promos() -> list[PromoCode]:
    async with get_session() as session:
        result = await session.execute(select(PromoCode).order_by(PromoCode.id.desc()))
        return list(result.scalars().all())


async def toggle_promo(promo_id: int) -> bool:
    async with get_session() as session:
        promo = await session.get(PromoCode, promo_id)
        if not promo:
            return False
        promo.is_active = not promo.is_active
        await session.commit()
        return True


async def delete_promo(promo_id: int) -> bool:
    async with get_session() as session:
        promo = await session.get(PromoCode, promo_id)
        if not promo:
            return False
        await session.delete(promo)
        await session.commit()
        return True
