"""Savat (Cart) bilan bog'liq operatsiyalar."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import CartItem, Product


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    async with get_session() as session:
        result = await session.execute(
            select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        )
        item = result.scalar_one_or_none()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


async def get_cart_items(user_id: int) -> list[CartItem]:
    async with get_session() as session:
        result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        )
        return list(result.scalars().all())


async def get_cart_item(item_id: int) -> CartItem | None:
    async with get_session() as session:
        result = await session.execute(
            select(CartItem).options(selectinload(CartItem.product)).where(CartItem.id == item_id)
        )
        return result.scalar_one_or_none()


async def change_quantity(item_id: int, delta: int) -> CartItem | None:
    """Savatdagi mahsulot sonini +1/-1 qilish. 0 ga tushsa o'chiriladi."""
    async with get_session() as session:
        item = await session.get(CartItem, item_id)
        if not item:
            return None
        item.quantity += delta
        if item.quantity <= 0:
            await session.delete(item)
            await session.commit()
            return None
        await session.commit()
        await session.refresh(item)
        return item


async def set_item_comment(item_id: int, comment: str) -> bool:
    async with get_session() as session:
        item = await session.get(CartItem, item_id)
        if not item:
            return False
        item.comment = comment
        await session.commit()
        return True


async def remove_item(item_id: int) -> bool:
    async with get_session() as session:
        item = await session.get(CartItem, item_id)
        if not item:
            return False
        await session.delete(item)
        await session.commit()
        return True


async def clear_cart(user_id: int) -> None:
    async with get_session() as session:
        result = await session.execute(select(CartItem).where(CartItem.user_id == user_id))
        for item in result.scalars().all():
            await session.delete(item)
        await session.commit()


async def get_cart_total(user_id: int) -> float:
    items = await get_cart_items(user_id)
    return sum(float(item.product.price) * item.quantity for item in items)
