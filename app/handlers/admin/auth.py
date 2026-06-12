"""Admin va xodimlar (ofitsiant/oshxona) uchun login (/admin, /staff)."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.services.admin_service import authenticate
from app.models.admin import StaffRole
from app.keyboards.admin_kb import admin_main_kb
from app.keyboards.staff_kb import waiter_main_kb, kitchen_main_kb
from app.keyboards.user_kb import main_menu_kb
from app.utils.states import AdminAuth, StaffAuth

router = Router(name="admin_auth")


# ---------------- ADMIN LOGIN ----------------
@router.message(Command("admin"))
async def admin_login_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminAuth.waiting_username)
    await message.answer("🔐 <b>Admin panel</b>\n\nUsername kiriting:")


@router.message(AdminAuth.waiting_username)
async def admin_login_username(message: Message, state: FSMContext) -> None:
    await state.update_data(login_username=message.text.strip())
    await state.set_state(AdminAuth.waiting_password)
    await message.answer("🔑 Parolni kiriting:")


@router.message(AdminAuth.waiting_password)
async def admin_login_password(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    username = data.get("login_username")
    password = message.text.strip()

    try:
        await message.delete()
    except Exception:
        pass

    staff = await authenticate(username, password, telegram_id=message.from_user.id)
    if not staff or staff.role != StaffRole.ADMIN:
        await message.answer("❌ Login yoki parol xato, yoki sizda admin huquqi yo'q.")
        await state.set_state(None)
        return

    await state.set_state(None)
    await state.update_data(staff_id=staff.id, staff_role="admin")
    await message.answer(
        f"✅ Xush kelibsiz, <b>{staff.full_name}</b>!\n\nAdmin paneliga xush kelibsiz.",
        reply_markup=admin_main_kb(),
    )


# ---------------- OFITSIANT / OSHXONA LOGIN ----------------
@router.message(Command("staff"))
async def staff_login_start(message: Message, state: FSMContext) -> None:
    await state.set_state(StaffAuth.waiting_username)
    await message.answer("🔐 <b>Xodim panel</b>\n\nUsername kiriting:")


@router.message(StaffAuth.waiting_username)
async def staff_login_username(message: Message, state: FSMContext) -> None:
    await state.update_data(login_username=message.text.strip())
    await state.set_state(StaffAuth.waiting_password)
    await message.answer("🔑 Parolni kiriting:")


@router.message(StaffAuth.waiting_password)
async def staff_login_password(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    username = data.get("login_username")
    password = message.text.strip()

    try:
        await message.delete()
    except Exception:
        pass

    staff = await authenticate(username, password, telegram_id=message.from_user.id)
    if not staff or staff.role == StaffRole.ADMIN:
        await message.answer("❌ Login yoki parol xato.")
        await state.set_state(None)
        return

    await state.set_state(None)
    await state.update_data(staff_id=staff.id, staff_role=staff.role.value)

    if staff.role == StaffRole.WAITER:
        await message.answer(
            f"✅ Xush kelibsiz, <b>{staff.full_name}</b>! (Ofitsiant)",
            reply_markup=waiter_main_kb(),
        )
    else:
        await message.answer(
            f"✅ Xush kelibsiz, <b>{staff.full_name}</b>! (Oshxona)",
            reply_markup=kitchen_main_kb(),
        )


# ---------------- CHIQISH ----------------
@router.message(F.text == "🚪 Chiqish")
async def staff_logout(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("staff_id"):
        await state.update_data(staff_id=None, staff_role=None)
        await message.answer("👋 Chiqdingiz.", reply_markup=main_menu_kb())
