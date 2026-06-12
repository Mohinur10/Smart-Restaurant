"""Admin: Stollar (QR kod linklari) boshqaruvi."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import admin_tables_kb
from app.services.table_service import get_all_tables, create_table
from app.utils.filters import IsAdmin

router = Router(name="admin_tables")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text == "🪑 Stollar")
async def list_tables(message: Message) -> None:
    tables = await get_all_tables()
    bot_info = await message.bot.get_me()

    if not tables:
        await message.answer("😔 Hozircha stollar yo'q.", reply_markup=admin_tables_kb())
        return

    lines = ["🪑 <b>Stollar va QR linklar:</b>", ""]
    for t in tables:
        link = f"https://t.me/{bot_info.username}?start=table_{t.qr_token}"
        lines.append(f"Stol {t.number}: {link}")

    await message.answer("\n".join(lines), reply_markup=admin_tables_kb())


@router.callback_query(F.data == "atable_new")
async def new_table(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(creating_table=True)
    await call.message.answer("🔢 Yangi stol raqamini kiriting:")
    await call.answer()


@router.message(F.text.regexp(r"^\d+$"))
async def new_table_number(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("creating_table"):
        return  # Boshqa raqamli xabarlarga aralashmaymiz

    number = int(message.text.strip())
    table = await create_table(number=number)
    await state.update_data(creating_table=False)

    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=table_{table.qr_token}"

    await message.answer(
        f"✅ Stol {table.number} qo'shildi!\n\n"
        f"🔗 QR link:\n<code>{link}</code>\n\n"
        "Bu linkdan QR kod generator orqali QR rasm yaratib, stol ustiga joylashtiring."
    )
