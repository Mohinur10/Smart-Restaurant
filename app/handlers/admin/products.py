"""Admin: Mahsulotlar CRUD."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import (
    admin_products_kb, admin_product_detail_kb, admin_categories_for_product_kb,
)
from app.services.category_service import get_all_categories, get_category
from app.services.product_service import (
    get_all_products, get_product, create_product,
    update_product_field, toggle_availability, delete_product,
)
from app.utils.callbacks import AdminCatCB, AdminProdCB
from app.utils.states import ProductForm
from app.utils.filters import IsAdmin

router = Router(name="admin_products")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _product_text(product) -> str:
    price_text = f"{int(product.price):,} so'm".replace(",", " ")
    status = "✅ Mavjud" if product.is_available else "❌ Mavjud emas"
    return (
        f"<b>{product.name}</b>\n\n"
        f"📂 Kategoriya: {product.category.display_name if product.category else '-'}\n"
        f"📝 Tavsif: {product.description or '-'}\n"
        f"💰 Narxi: {price_text}\n"
        f"⏱ Tayyorlanish vaqti: {product.cook_time_minutes} daq.\n"
        f"🔢 Soni: {product.quantity}\n"
        f"🏷 Kodi: {product.product_code or '-'}\n"
        f"📦 Holati: {status}"
    )


@router.message(F.text == "📦 Mahsulotlar")
async def list_products(message: Message) -> None:
    products = await get_all_products()
    if not products:
        await message.answer("😔 Hozircha mahsulot yo'q.", reply_markup=admin_products_kb(products))
        return
    await message.answer("📦 <b>Mahsulotlar:</b>", reply_markup=admin_products_kb(products))


@router.callback_query(F.data == "aprod_list")
async def back_to_products(call: CallbackQuery) -> None:
    products = await get_all_products()
    await call.message.edit_text("📦 <b>Mahsulotlar:</b>", reply_markup=admin_products_kb(products))
    await call.answer()


@router.callback_query(AdminProdCB.filter(F.action == "view"))
async def view_product(call: CallbackQuery, callback_data: AdminProdCB) -> None:
    product = await get_product(callback_data.id)
    if not product:
        await call.answer("Topilmadi", show_alert=True)
        return

    text = _product_text(product)
    kb = admin_product_detail_kb(product)

    if product.image_file_id:
        await call.message.delete()
        await call.message.answer_photo(photo=product.image_file_id, caption=text, reply_markup=kb)
    else:
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)
    await call.answer()


@router.callback_query(AdminProdCB.filter(F.action == "toggle"))
async def toggle_product(call: CallbackQuery, callback_data: AdminProdCB) -> None:
    await toggle_availability(callback_data.id)
    product = await get_product(callback_data.id)
    await call.answer("Holat o'zgartirildi")
    await call.message.answer(_product_text(product), reply_markup=admin_product_detail_kb(product))


@router.callback_query(AdminProdCB.filter(F.action == "delete"))
async def delete_product_handler(call: CallbackQuery, callback_data: AdminProdCB) -> None:
    await delete_product(callback_data.id)
    products = await get_all_products()
    await call.message.answer("🗑 O'chirildi.")
    await call.message.answer("📦 <b>Mahsulotlar:</b>", reply_markup=admin_products_kb(products))
    await call.answer()


# ---------------- YANGI MAHSULOT ----------------
@router.callback_query(F.data == "aprod_new")
async def new_product_start(call: CallbackQuery, state: FSMContext) -> None:
    categories = await get_all_categories()
    if not categories:
        await call.answer("Avval kategoriya yarating!", show_alert=True)
        return
    await state.set_state(ProductForm.waiting_category)
    await call.message.answer("📂 Kategoriyani tanlang:", reply_markup=admin_categories_for_product_kb(categories))
    await call.answer()


@router.callback_query(ProductForm.waiting_category, AdminCatCB.filter(F.action == "pick"))
async def new_product_category(call: CallbackQuery, callback_data: AdminCatCB, state: FSMContext) -> None:
    await state.update_data(new_prod_category_id=callback_data.id)
    await state.set_state(ProductForm.waiting_name)
    await call.message.answer("📝 Mahsulot nomini kiriting:")
    await call.answer()


@router.message(ProductForm.waiting_name)
async def new_product_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_prod_name=message.text.strip())
    await state.set_state(ProductForm.waiting_description)
    await message.answer("📝 Tarkibi / tavsifini kiriting (yoki '-' o'tkazib yuborish uchun):")


@router.message(ProductForm.waiting_description)
async def new_product_description(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    await state.update_data(new_prod_description=None if text == "-" else text)
    await state.set_state(ProductForm.waiting_price)
    await message.answer("💰 Narxini kiriting (so'mda, faqat raqam):")


@router.message(ProductForm.waiting_price)
async def new_product_price(message: Message, state: FSMContext) -> None:
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting.")
        return
    await state.update_data(new_prod_price=int(text))
    await state.set_state(ProductForm.waiting_image)
    await message.answer("🖼 Mahsulot rasmini yuboring (yoki '-' o'tkazib yuborish uchun):")


@router.message(ProductForm.waiting_image, F.photo)
async def new_product_image(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(new_prod_image=file_id)
    await state.set_state(ProductForm.waiting_cook_time)
    await message.answer("⏱ Tayyorlanish vaqtini kiriting (daqiqada, raqam):")


@router.message(ProductForm.waiting_image, F.text == "-")
async def new_product_image_skip(message: Message, state: FSMContext) -> None:
    await state.update_data(new_prod_image=None)
    await state.set_state(ProductForm.waiting_cook_time)
    await message.answer("⏱ Tayyorlanish vaqtini kiriting (daqiqada, raqam):")


@router.message(ProductForm.waiting_image)
async def new_product_image_invalid(message: Message) -> None:
    await message.answer("⚠️ Rasm yuboring yoki '-' yozing.")


@router.message(ProductForm.waiting_cook_time)
async def new_product_cook_time(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting.")
        return
    await state.update_data(new_prod_cook_time=int(text))
    await state.set_state(ProductForm.waiting_quantity)
    await message.answer("🔢 Mavjud miqdorini kiriting (sklad soni):")


@router.message(ProductForm.waiting_quantity)
async def new_product_quantity(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting.")
        return
    await state.update_data(new_prod_quantity=int(text))
    await state.set_state(ProductForm.waiting_code)
    await message.answer("🏷 Mahsulot kodini kiriting (yoki '-' o'tkazib yuborish uchun):")


@router.message(ProductForm.waiting_code)
async def new_product_code(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    code = None if text == "-" else text

    data = await state.get_data()
    quantity = data["new_prod_quantity"]

    product = await create_product(
        category_id=data["new_prod_category_id"],
        name=data["new_prod_name"],
        description=data.get("new_prod_description"),
        price=data["new_prod_price"],
        image_file_id=data.get("new_prod_image"),
        cook_time_minutes=data["new_prod_cook_time"],
        quantity=quantity,
        product_code=code,
        is_available=quantity > 0,
    )

    await state.set_state(None)
    await message.answer(f"✅ Mahsulot yaratildi: <b>{product.name}</b>")

    products = await get_all_products()
    await message.answer("📦 <b>Mahsulotlar:</b>", reply_markup=admin_products_kb(products))


# ---------------- MAHSULOTNI TAHRIRLASH ----------------
FIELD_PROMPTS = {
    "name": "📝 Yangi nomni kiriting:",
    "description": "📝 Yangi tavsifni kiriting:",
    "price": "💰 Yangi narxni kiriting (raqam):",
    "image_file_id": "🖼 Yangi rasmni yuboring:",
    "cook_time_minutes": "⏱ Yangi tayyorlanish vaqtini kiriting (daqiqa):",
    "quantity": "🔢 Yangi miqdorni kiriting:",
    "product_code": "🏷 Yangi kodni kiriting:",
}


@router.callback_query(AdminProdCB.filter(F.action == "edit_field"))
async def edit_product_field_start(call: CallbackQuery, callback_data: AdminProdCB, state: FSMContext) -> None:
    await state.update_data(editing_prod_id=callback_data.id, editing_prod_field=callback_data.field)
    await state.set_state(ProductForm.editing_value)
    await call.message.answer(FIELD_PROMPTS.get(callback_data.field, "Yangi qiymatni kiriting:"))
    await call.answer()


@router.message(ProductForm.editing_value, F.photo)
async def edit_product_field_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("editing_prod_field") != "image_file_id":
        await message.answer("⚠️ Bu maydon uchun matn kiriting.")
        return
    await _save_field(message, state, message.photo[-1].file_id)


@router.message(ProductForm.editing_value)
async def edit_product_field_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data.get("editing_prod_field")
    text = message.text.strip()

    if field in ("price", "cook_time_minutes", "quantity"):
        clean = text.replace(" ", "")
        if not clean.isdigit():
            await message.answer("⚠️ Faqat raqam kiriting.")
            return
        value = int(clean)
    else:
        value = text

    await _save_field(message, state, value)


async def _save_field(message: Message, state: FSMContext, value) -> None:
    data = await state.get_data()
    product_id = data.get("editing_prod_id")
    field = data.get("editing_prod_field")

    await update_product_field(product_id, field, value)
    await state.set_state(None)

    product = await get_product(product_id)
    await message.answer("✅ Yangilandi.")
    await message.answer(_product_text(product), reply_markup=admin_product_detail_kb(product))
