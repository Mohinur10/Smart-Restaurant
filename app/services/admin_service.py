"""Xodimlar (Admin/Ofitsiant/Oshxona) bilan bog'liq operatsiyalar."""
from sqlalchemy import select

from app.database import get_session
from app.models import Admin
from app.models.admin import StaffRole
from app.utils.security import hash_password, verify_password


async def get_staff_by_username(username: str) -> Admin | None:
    async with get_session() as session:
        result = await session.execute(select(Admin).where(Admin.username.ilike(username)))
        return result.scalar_one_or_none()


async def get_staff_by_telegram_id(telegram_id: int) -> Admin | None:
    async with get_session() as session:
        result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        return result.scalar_one_or_none()


async def authenticate(username: str, password: str, telegram_id: int) -> Admin | None:
    """Username/parol to'g'ri bo'lsa, telegram_id ni saqlab Admin obyektini qaytaradi."""
    staff = await get_staff_by_username(username)
    if not staff or not staff.is_active:
        return None
    if not verify_password(password, staff.password_hash):
        return None

    async with get_session() as session:
        # Boshqa akkauntda ushbu telegram_id bo'lsa, uni tozalaymiz (xatolik bermasligi uchun)
        result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        existing_owner = result.scalar_one_or_none()
        if existing_owner and existing_owner.id != staff.id:
            existing_owner.telegram_id = None

        db_staff = await session.get(Admin, staff.id)
        db_staff.telegram_id = telegram_id
        await session.commit()
        await session.refresh(db_staff)
        return db_staff


async def create_staff(username: str, password: str, full_name: str, role: StaffRole) -> Admin | None:
    existing = await get_staff_by_username(username)
    if existing:
        return None
    async with get_session() as session:
        staff = Admin(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        session.add(staff)
        await session.commit()
        await session.refresh(staff)
        return staff


async def get_staff_by_role(role: StaffRole) -> list[Admin]:
    async with get_session() as session:
        result = await session.execute(select(Admin).where(Admin.role == role, Admin.is_active == True))  # noqa: E712
        return list(result.scalars().all())


async def get_all_staff() -> list[Admin]:
    async with get_session() as session:
        result = await session.execute(select(Admin).order_by(Admin.role, Admin.id))
        return list(result.scalars().all())


async def toggle_staff(staff_id: int) -> bool:
    async with get_session() as session:
        staff = await session.get(Admin, staff_id)
        if not staff:
            return False
        staff.is_active = not staff.is_active
        await session.commit()
        return True


async def delete_staff(staff_id: int) -> bool:
    async with get_session() as session:
        staff = await session.get(Admin, staff_id)
        if not staff:
            return False
        await session.delete(staff)
        await session.commit()
        return True


async def ensure_super_admin(username: str, password: str) -> None:
    """.env dagi ADMIN_USERNAME/ADMIN_PASSWORD bo'yicha bosh adminni yaratib qo'yadi."""
    existing = await get_staff_by_username(username)
    if existing:
        return
    await create_staff(username=username, password=password, full_name="Bosh admin", role=StaffRole.ADMIN)
