"""Menyu: kategoriyalar -> mahsulotlar -> mahsulot kartasi."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.user_kb import categories_kb, products_kb, product_card_kb
from app.services.category_service import get_active_categories, get_category
from app.services.product_service import get_products_by_category, get_product
from app.services.cart_service import add_to_cart
from app.services.favorite_service import is_favorite, toggle_favorite
from app.utils.callbacks import CategoryCB, ProductCB, CartAddCB, FavoriteCB

router = Router(name="user_menu")


@router.message(F.text == "📋 Menyu")
async def show_menu(message: Message) -> None:
    categories = await get_active_categories()
    if not categories:
        await message.answer("😔 Hozircha kategoriyalar mavjud emas.")
        return
    await message.answer("🍽 <b>Menyu bo'limlari:</b>", reply_markup=categories_kb(categories))


@router.callback_query(CategoryCB.filter())
async def show_category_products(call: CallbackQuery, callback_data: CategoryCB) -> None:
    category = await get_category(callback_data.id)
    if not category:
        await call.answer("Kategoriya topilmadi", show_alert=True)
        return

    products = await get_products_by_category(callback_data.id)
    if not products:
        await call.message.edit_text(
            f"{category.display_name}\n\n😔 Hozircha mahsulotlar yo'q.",
            reply_markup=products_kb(products, callback_data.id),
        )
        await call.answer()
        return

    await call.message.edit_text(
        f"{category.display_name}\n\nMahsulotni tanlang 👇",
        reply_markup=products_kb(products, callback_data.id),
    )
    await call.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(call: CallbackQuery) -> None:
    categories = await get_active_categories()
    await call.message.edit_text("🍽 <b>Menyu bo'limlari:</b>", reply_markup=categories_kb(categories))
    await call.answer()


@router.callback_query(ProductCB.filter())
async def show_product(call: CallbackQuery, callback_data: ProductCB, state: FSMContext) -> None:
    product = await get_product(callback_data.id)
    if not product:
        await call.answer("Mahsulot topilmadi", show_alert=True)
        return

    data = await state.get_data()
    user_id = data.get("user_id")
    fav = await is_favorite(user_id, product.id) if user_id else False

    availability = "✅ Mavjud" if product.is_available and product.quantity > 0 else "❌ Mavjud emas"
    price_text = f"{int(product.price):,} so'm".replace(",", " ")

    caption = (
        f"<b>{product.name}</b>\n\n"
        f"📝 {product.description or '—'}\n\n"
        f"💰 Narxi: {price_text}\n"
        f"⏱ Tayyor bo'lish vaqti: {product.cook_time_minutes} daq.\n"
        f"📦 Holati: {availability}"
    )

    kb = product_card_kb(product, fav)

    if product.image_file_id:
        await call.message.delete()
        await call.message.answer_photo(photo=product.image_file_id, caption=caption, reply_markup=kb)
    else:
        await call.message.edit_text(caption, reply_markup=kb)

    await call.answer()


@router.callback_query(CartAddCB.filter())
async def add_product_to_cart(call: CallbackQuery, callback_data: CartAddCB, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        await call.answer("Iltimos, /start bosing", show_alert=True)
        return

    product = await get_product(callback_data.product_id)
    if not product or not product.is_available or product.quantity <= 0:
        await call.answer("😔 Bu mahsulot hozir mavjud emas", show_alert=True)
        return

    await add_to_cart(user_id, callback_data.product_id)
    await call.answer("🛒 Savatga qo'shildi!")


@router.callback_query(FavoriteCB.filter())
async def toggle_fav(call: CallbackQuery, callback_data: FavoriteCB, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        await call.answer("Iltimos, /start bosing", show_alert=True)
        return

    added = await toggle_favorite(user_id, callback_data.product_id)
    product = await get_product(callback_data.product_id)

    kb = product_card_kb(product, added)
    try:
        await call.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass

    await call.answer("❤️ Saqlandi" if added else "💔 Saqlanganlardan olib tashlandi")
