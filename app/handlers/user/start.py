"""Foydalanuvchi uchun /start handler — QR kod orqali stolni aniqlash."""
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.user_kb import main_menu_kb
from app.services.user_service import get_or_create_user
from app.services.table_service import get_table_by_token

router = Router(name="user_start")


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext) -> None:
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    await state.update_data(user_id=user.id)

    # Deep-link: https://t.me/<bot>?start=table_<qr_token>
    args = command.args
    if args and args.startswith("table_"):
        token = args.removeprefix("table_")
        table = await get_table_by_token(token)
        if table:
            await state.update_data(table_id=table.id, table_number=table.number)
            await message.answer(
                f"👋 Xush kelibsiz!\n\n📍 Siz <b>{table.number}-stoldasiz</b>.",
                reply_markup=main_menu_kb(),
            )
            return
        else:
            await message.answer("⚠️ QR kod noto'g'ri yoki eskirgan. Iltimos, ofitsiantga murojaat qiling.")

    await message.answer(
        "👋 Assalomu alaykum!\n\nSmart Restaurant botiga xush kelibsiz.\n"
        "Buyurtma berish uchun stol ustidagi QR kodni skaner qiling.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "🚪 Chiqish")
async def exit_to_main(message: Message, state: FSMContext) -> None:
    """Admin/ofitsiant/oshxona panelidan asosiy menyuga qaytish."""
    await state.clear()
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu_kb())
