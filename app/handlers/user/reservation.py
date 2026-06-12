"""Stol band qilish (Reservation) oqimi."""
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database import get_session
from app.models import Reservation, Table
from app.services.table_service import get_all_tables, get_table_by_id
from app.services.user_service import set_user_phone
from app.utils.states import ReservationForm
from app.keyboards.user_kb import main_menu_kb

router = Router(name="user_reservation")


@router.message(F.text == "📅 Stol band qilish")
async def start_reservation(message: Message, state: FSMContext) -> None:
    tables = await get_all_tables()
    if not tables:
        await message.answer("😔 Hozircha stollar ro'yxati mavjud emas.")
        return

    builder = InlineKeyboardBuilder()
    for t in tables:
        builder.button(text=f"🪑 Stol {t.number}", callback_data=f"resv_table_{t.id}")
    builder.adjust(3)

    await state.set_state(ReservationForm.choosing_table)
    await message.answer("Qaysi stolni band qilmoqchisiz?", reply_markup=builder.as_markup())


@router.callback_query(ReservationForm.choosing_table, F.data.startswith("resv_table_"))
async def choose_table(call, state: FSMContext) -> None:
    table_id = int(call.data.removeprefix("resv_table_"))
    table = await get_table_by_id(table_id)
    if not table:
        await call.answer("Stol topilmadi", show_alert=True)
        return

    await state.update_data(reservation_table_id=table_id, reservation_table_number=table.number)
    await state.set_state(ReservationForm.entering_datetime)
    await call.message.answer(
        f"🪑 Stol {table.number} tanlandi.\n\n"
        "📅 Qaysi sana va soatga band qilmoqchisiz?\n"
        "Masalan: <code>2026-06-15 19:30</code>"
    )
    await call.answer()


@router.message(ReservationForm.entering_datetime)
async def enter_datetime(message: Message, state: FSMContext) -> None:
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("⚠️ Format noto'g'ri. Masalan: <code>2026-06-15 19:30</code>")
        return

    await state.update_data(reservation_datetime=dt)
    await state.set_state(ReservationForm.entering_guests)
    await message.answer("👥 Necha kishi bo'lasiz?")


@router.message(ReservationForm.entering_guests)
async def enter_guests(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("⚠️ Iltimos, musbat raqam kiriting.")
        return
    await state.update_data(reservation_guests=int(text))
    await state.set_state(ReservationForm.entering_phone)
    await message.answer("📞 Bog'lanish uchun telefon raqamingizni kiriting:")


@router.message(ReservationForm.entering_phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")

    await set_user_phone(user_id, phone)

    async with get_session() as session:
        reservation = Reservation(
            user_id=user_id,
            table_id=data["reservation_table_id"],
            guests_count=data["reservation_guests"],
            reserved_at=data["reservation_datetime"],
            phone=phone,
        )
        session.add(reservation)
        await session.commit()

    dt: datetime = data["reservation_datetime"]
    await message.answer(
        f"✅ <b>Rezervatsiya qabul qilindi!</b>\n\n"
        f"🪑 Stol: {data['reservation_table_number']}\n"
        f"📅 Vaqt: {dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"👥 Kishi soni: {data['reservation_guests']}\n\n"
        "Restoran sizni kutib qoladi! 😊",
        reply_markup=main_menu_kb(),
    )
    await state.set_state(None)
