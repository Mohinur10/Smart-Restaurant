"""Admin: Kategoriyalar CRUD."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import admin_categories_kb, admin_category_detail_kb
from app.services.category_service import (
    get_all_categories, get_category, create_category,
    update_category_name, toggle_category, delete_category,
)
from app.utils.callbacks import AdminCatCB
from app.utils.states import CategoryForm
from app.utils.filters import IsAdmin

router = Router(name="admin_categories")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text == "📂 Kategoriyalar")
async def list_categories(message: Message) -> None:
    categories = await get_all_categories()
    await message.answer("📂 <b>Kategoriyalar:</b>", reply_markup=admin_categories_kb(categories))


@router.callback_query(F.data == "acat_list")
async def back_to_list(call: CallbackQuery) -> None:
    categories = await get_all_categories()
    await call.message.edit_text("📂 <b>Kategoriyalar:</b>", reply_markup=admin_categories_kb(categories))
    await call.answer()


@router.callback_query(AdminCatCB.filter(F.action == "view"))
async def view_category(call: CallbackQuery, callback_data: AdminCatCB) -> None:
    category = await get_category(callback_data.id)
    if not category:
        await call.answer("Topilmadi", show_alert=True)
        return

    status = "✅ Faol" if category.is_active else "🚫 Faol emas"
    text = f"{category.display_name}\n\nHolat: {status}"
    await call.message.edit_text(text, reply_markup=admin_category_detail_kb(category))
    await call.answer()


@router.callback_query(F.data == "acat_new")
async def new_category_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CategoryForm.waiting_name)
    await call.message.answer("📝 Yangi kategoriya nomini kiriting (masalan: Ovqatlar):")
    await call.answer()


@router.message(CategoryForm.waiting_name)
async def new_category_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_cat_name=message.text.strip())
    await state.set_state(CategoryForm.waiting_emoji)
    await message.answer("😀 Endi emoji yuboring (masalan: 🍔), yoki '-' yozing agar kerak bo'lmasa:")


@router.message(CategoryForm.waiting_emoji)
async def new_category_emoji(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data.get("new_cat_name")
    emoji_text = message.text.strip()
    emoji = None if emoji_text == "-" else emoji_text

    category = await create_category(name=name, emoji=emoji)
    await state.set_state(None)

    categories = await get_all_categories()
    await message.answer(f"✅ Kategoriya yaratildi: {category.display_name}")
    await message.answer("📂 <b>Kategoriyalar:</b>", reply_markup=admin_categories_kb(categories))


@router.callback_query(AdminCatCB.filter(F.action == "edit"))
async def edit_category_start(call: CallbackQuery, callback_data: AdminCatCB, state: FSMContext) -> None:
    await state.update_data(editing_cat_id=callback_data.id)
    await state.set_state(CategoryForm.editing_name)
    await call.message.answer("✏️ Yangi nomni kiriting:")
    await call.answer()


@router.message(CategoryForm.editing_name)
async def edit_category_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    cat_id = data.get("editing_cat_id")
    await update_category_name(cat_id, message.text.strip())
    await state.set_state(None)

    categories = await get_all_categories()
    await message.answer("✅ Yangilandi.")
    await message.answer("📂 <b>Kategoriyalar:</b>", reply_markup=admin_categories_kb(categories))


@router.callback_query(AdminCatCB.filter(F.action == "toggle"))
async def toggle_category_handler(call: CallbackQuery, callback_data: AdminCatCB) -> None:
    await toggle_category(callback_data.id)
    category = await get_category(callback_data.id)
    status = "✅ Faol" if category.is_active else "🚫 Faol emas"
    text = f"{category.display_name}\n\nHolat: {status}"
    await call.message.edit_text(text, reply_markup=admin_category_detail_kb(category))
    await call.answer("Holat o'zgartirildi")


@router.callback_query(AdminCatCB.filter(F.action == "delete"))
async def delete_category_handler(call: CallbackQuery, callback_data: AdminCatCB) -> None:
    await delete_category(callback_data.id)
    categories = await get_all_categories()
    await call.message.edit_text("🗑 O'chirildi.\n\n📂 <b>Kategoriyalar:</b>", reply_markup=admin_categories_kb(categories))
    await call.answer()
