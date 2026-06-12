"""Reyting (Rating) bilan ishlash."""
from sqlalchemy import select

from app.database import get_session
from app.models import Rating, OrderItem, Order


async def add_rating(user_id: int, order_id: int, product_id: int, stars: int, comment: str | None = None) -> Rating:
    async with get_session() as session:
        result = await session.execute(
            select(Rating).where(Rating.order_id == order_id, Rating.product_id == product_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.stars = stars
            existing.comment = comment
            await session.commit()
            await session.refresh(existing)
            return existing

        rating = Rating(user_id=user_id, order_id=order_id, product_id=product_id, stars=stars, comment=comment)
        session.add(rating)
        await session.commit()
        await session.refresh(rating)
        return rating


async def get_order_products_to_rate(order_id: int) -> list[OrderItem]:
    """Buyurtma ichidagi mahsulotlar ro'yxati (baholash uchun)."""
    async with get_session() as session:
        order = await session.get(Order, order_id)
        if not order:
            return []
        result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
        return list(result.scalars().all())
