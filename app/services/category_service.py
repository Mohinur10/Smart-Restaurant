"""Kategoriya (Category) CRUD operatsiyalari."""
from sqlalchemy import select

from app.database import get_session
from app.models import Category


async def get_active_categories() -> list[Category]:
    async with get_session() as session:
        result = await session.execute(
            select(Category).where(Category.is_active == True).order_by(Category.position, Category.id)  # noqa: E712
        )
        return list(result.scalars().all())


async def get_all_categories() -> list[Category]:
    async with get_session() as session:
        result = await session.execute(select(Category).order_by(Category.position, Category.id))
        return list(result.scalars().all())


async def get_category(category_id: int) -> Category | None:
    async with get_session() as session:
        return await session.get(Category, category_id)


async def create_category(name: str, emoji: str | None = None) -> Category:
    async with get_session() as session:
        category = Category(name=name, emoji=emoji)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


async def update_category_name(category_id: int, name: str) -> bool:
    async with get_session() as session:
        category = await session.get(Category, category_id)
        if not category:
            return False
        category.name = name
        await session.commit()
        return True


async def toggle_category(category_id: int) -> bool:
    async with get_session() as session:
        category = await session.get(Category, category_id)
        if not category:
            return False
        category.is_active = not category.is_active
        await session.commit()
        return True


async def delete_category(category_id: int) -> bool:
    async with get_session() as session:
        category = await session.get(Category, category_id)
        if not category:
            return False
        await session.delete(category)
        await session.commit()
        return True
