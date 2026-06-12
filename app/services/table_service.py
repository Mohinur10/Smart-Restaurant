"""Stol (Table) bilan bog'liq operatsiyalar — QR kod orqali aniqlash."""
import secrets

from sqlalchemy import select

from app.database import get_session
from app.models import Table


async def get_table_by_token(qr_token: str) -> Table | None:
    async with get_session() as session:
        result = await session.execute(select(Table).where(Table.qr_token == qr_token, Table.is_active == True))  # noqa: E712
        return result.scalar_one_or_none()


async def get_table_by_id(table_id: int) -> Table | None:
    async with get_session() as session:
        return await session.get(Table, table_id)


async def get_all_tables() -> list[Table]:
    async with get_session() as session:
        result = await session.execute(select(Table).order_by(Table.number))
        return list(result.scalars().all())


async def create_table(number: int, branch_id: int | None = None) -> Table:
    """Yangi stol yaratadi va unga noyob QR token beradi.

    QR kod generatsiya qilish uchun foydalanuvchi botga
    `https://t.me/<bot_username>?start=table_<qr_token>` linkidan kirishi kerak.
    """
    async with get_session() as session:
        table = Table(number=number, branch_id=branch_id, qr_token=secrets.token_urlsafe(8))
        session.add(table)
        await session.commit()
        await session.refresh(table)
        return table


async def delete_table(table_id: int) -> bool:
    async with get_session() as session:
        table = await session.get(Table, table_id)
        if not table:
            return False
        await session.delete(table)
        await session.commit()
        return True
