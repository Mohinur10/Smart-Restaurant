"""Mahsulot (Product) CRUD, qidiruv va boshqa operatsiyalar."""
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Product, Category


async def get_products_by_category(category_id: int, only_available: bool = True) -> list[Product]:
    async with get_session() as session:
        stmt = select(Product).where(Product.category_id == category_id)
        if only_available:
            stmt = stmt.where(Product.is_available == True)  # noqa: E712
        stmt = stmt.order_by(Product.id)
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def get_all_products() -> list[Product]:
    async with get_session() as session:
        result = await session.execute(
            select(Product).options(selectinload(Product.category)).order_by(Product.id)
        )
        return list(result.scalars().all())


async def get_product(product_id: int) -> Product | None:
    async with get_session() as session:
        result = await session.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()


async def search_products(query: str) -> list[Product]:
    """Nomi, tavsifi yoki kodi bo'yicha qidirish."""
    pattern = f"%{query.strip()}%"
    async with get_session() as session:
        stmt = (
            select(Product)
            .where(
                Product.is_available == True,  # noqa: E712
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                    Product.product_code.ilike(pattern),
                ),
            )
            .order_by(Product.id)
            .limit(20)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def create_product(**kwargs) -> Product:
    async with get_session() as session:
        product = Product(**kwargs)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product


async def update_product_field(product_id: int, field: str, value) -> bool:
    """Mahsulotning bitta maydonini yangilash (admin tahrirlash uchun)."""
    allowed_fields = {
        "name", "description", "price", "image_file_id",
        "cook_time_minutes", "quantity", "product_code",
    }
    if field not in allowed_fields:
        return False

    async with get_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return False
        setattr(product, field, value)
        await session.commit()
        return True


async def toggle_availability(product_id: int) -> bool:
    async with get_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return False
        product.is_available = not product.is_available
        await session.commit()
        return True


async def decrease_quantity(product_id: int, amount: int) -> None:
    """Buyurtma berilganda mahsulot sonini kamaytirish. 0 ga tushsa - mavjud emas qiladi."""
    async with get_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return
        product.quantity = max(0, product.quantity - amount)
        if product.quantity == 0:
            product.is_available = False
        await session.commit()


async def delete_product(product_id: int) -> bool:
    async with get_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return False
        await session.delete(product)
        await session.commit()
        return True
