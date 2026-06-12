"""Admin: Xodimlar (Ofitsiant/Oshxona) boshqaruvi."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import admin_staff_main_kb, admin_staff_list_kb, admin_staff_detail_kb
from app.services.admin_service import create_staff, get_all_staff, get_staff_by_username, toggle_staff, delete_staff
from app.models.admin import StaffRole
from app.utils.callbacks import AdminStaffCB
from app.utils.states import StaffForm
from app.utils.filters import IsAdmin

router = Router(name="admin_staff")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

ROLE_TEXT = {"admin": "👑 Admin", "waiter": "🧑‍💼 Ofitsiant", "kitchen": "👨‍🍳 Oshxona"}


@router.message(F.text == "👥 Xodimlar")
async def staff_menu(message: Message) -> None:
    await message.answer("👥 <b>Xodimlar boshqaruvi:</b>", reply_markup=admin_staff_main_kb())


@router.callback_query(F.data.in_({"astaff_add_waiter", "astaff_add_kitchen"}))
async def add_staff_start(call: CallbackQuery, state: FSMContext) -> None:
    role = StaffRole.WAITER if call.data == "astaff_add_waiter" else StaffRole.KITCHEN
    await state.update_data(new_staff_role=role.value)
    await state.set_state(StaffForm.waiting_full_name)
    await call.message.answer("👤 Xodimning to'liq ismini kiriting:")
    await call.answer()


@router.message(StaffForm.waiting_full_name)
async def add_staff_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_staff_name=message.text.strip())
    await state.set_state(StaffForm.waiting_username)
    await message.answer("🔑 Login (username) kiriting:")


@router.message(StaffForm.waiting_username)
async def add_staff_username(message: Message, state: FSMContext) -> None:
    username = message.text.strip()
    existing = await get_staff_by_username(username)
    if existing:
        await message.answer("⚠️ Bu username band. Boshqasini kiriting:")
        return
    await state.update_data(new_staff_username=username)
    await state.set_state(StaffForm.waiting_password)
    await message.answer("🔐 Parol kiriting:")


@router.message(StaffForm.waiting_password)
async def add_staff_password(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    password = message.text.strip()

    try:
        await message.delete()
    except Exception:
        pass

    role = StaffRole(data["new_staff_role"])
    staff = await create_staff(
        username=data["new_staff_username"],
        password=password,
        full_name=data["new_staff_name"],
        role=role,
    )
    await state.set_state(None)

    if not staff:
        await message.answer("❌ Xatolik yuz berdi.")
        return

    role_text = "ofitsiant" if role == StaffRole.WAITER else "oshpaz"
    await message.answer(
        f"✅ Yangi {role_text} qo'shildi!\n\n"
        f"👤 Ism: {staff.full_name}\n"
        f"🔑 Login: <code>{staff.username}</code>\n\n"
        f"Xodim botga kirib <code>/staff</code> buyrug'i orqali shu login va parol bilan kirsin."
    )


@router.callback_query(F.data == "astaff_list")
async def staff_list(call: CallbackQuery) -> None:
    staff_list = await get_all_staff()
    if not staff_list:
        await call.answer("Xodimlar yo'q", show_alert=True)
        return
    await call.message.answer("📋 <b>Xodimlar ro'yxati:</b>", reply_markup=admin_staff_list_kb(staff_list))
    await call.answer()


@router.callback_query(AdminStaffCB.filter(F.action == "view"))
async def staff_detail(call: CallbackQuery, callback_data: AdminStaffCB) -> None:
    from app.database import get_session
    from app.models import Admin

    async with get_session() as session:
        staff = await session.get(Admin, callback_data.id)

    if not staff:
        await call.answer("Topilmadi", show_alert=True)
        return

    role_text = ROLE_TEXT.get(staff.role.value if hasattr(staff.role, "value") else staff.role, staff.role)
    status = "✅ Aktiv" if staff.is_active else "🚫 Bloklangan"
    text = (
        f"<b>{staff.full_name}</b>\n"
        f"Login: <code>{staff.username}</code>\n"
        f"Rol: {role_text}\n"
        f"Holat: {status}"
    )
    await call.message.edit_text(text, reply_markup=admin_staff_detail_kb(staff))
    await call.answer()


@router.callback_query(AdminStaffCB.filter(F.action == "toggle"))
async def staff_toggle(call: CallbackQuery, callback_data: AdminStaffCB) -> None:
    await toggle_staff(callback_data.id)
    await staff_detail(call, callback_data)
    await call.answer("Holat o'zgartirildi")


@router.callback_query(AdminStaffCB.filter(F.action == "delete"))
async def staff_delete(call: CallbackQuery, callback_data: AdminStaffCB) -> None:
    await delete_staff(callback_data.id)
    staff_list = await get_all_staff()
    await call.message.edit_text("🗑 O'chirildi.\n\n📋 <b>Xodimlar ro'yxati:</b>", reply_markup=admin_staff_list_kb(staff_list))
    await call.answer()
