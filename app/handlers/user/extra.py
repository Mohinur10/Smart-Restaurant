"""Qo'shimcha user funksiyalari: saqlanganlar, qidiruv, tarix, bonus, ofitsiant chaqirish, reyting."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.user_kb import rating_kb
from app.services.favorite_service import get_user_favorites
from app.services.product_service import search_products
from app.services.order_service import get_user_orders, get_order
from app.services.user_service import get_user_by_id
from app.services.rating_service import add_rating
from app.services.notify_service import notify_waiter_called
from app.models.order import OrderStatus
from app.utils.callbacks import ProductCB, CallWaiterCB, RatingCB
from app.utils.states import SearchProduct

router = Router(name="user_extra")


# ---------------- SAQLANGANLAR ----------------
@router.message(F.text == "❤️ Saqlanganlar")
async def show_favorites(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    favorites = await get_user_favorites(user_id)

    if not favorites:
        await message.answer("😔 Saqlangan mahsulotlar yo'q.")
        return

    builder = InlineKeyboardBuilder()
    for fav in favorites:
        p = fav.product
        price_text = f"{int(p.price):,} so'm".replace(",", " ")
        builder.button(text=f"{p.name} — {price_text}", callback_data=ProductCB(id=p.id))
    builder.adjust(1)

    await message.answer("❤️ <b>Saqlangan mahsulotlar:</b>", reply_markup=builder.as_markup())


# ---------------- QIDIRISH ----------------
@router.message(F.text == "🔍 Qidirish")
async def ask_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchProduct.waiting_query)
    await message.answer("🔍 Mahsulot nomi, kodi yoki tarkibini kiriting:")


@router.message(SearchProduct.waiting_query)
async def do_search(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    query = message.text.strip()
    results = await search_products(query)

    if not results:
        await message.answer("😔 Hech narsa topilmadi.")
        return

    builder = InlineKeyboardBuilder()
    for p in results:
        price_text = f"{int(p.price):,} so'm".replace(",", " ")
        builder.button(text=f"{p.name} — {price_text}", callback_data=ProductCB(id=p.id))
    builder.adjust(1)

    await message.answer(f"🔍 Natijalar ({len(results)}):", reply_markup=builder.as_markup())


# ---------------- BUYURTMALAR TARIXI ----------------
@router.message(F.text == "📦 Buyurtmalarim")
async def show_orders(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    orders = await get_user_orders(user_id)

    if not orders:
        await message.answer("😔 Hozircha buyurtmalar yo'q.")
        return

    status_emoji = {
        OrderStatus.NEW: "🆕 Yangi",
        OrderStatus.PREPARING: "👨‍🍳 Tayyorlanmoqda",
        OrderStatus.READY: "✅ Tayyor",
        OrderStatus.SERVED: "🍽 Yetkazildi",
        OrderStatus.CANCELLED: "❌ Bekor qilindi",
    }

    for order in orders:
        lines = [f"<b>Buyurtma #{order.id}</b>", f"Holat: {status_emoji.get(order.status, order.status)}", ""]
        for item in order.items:
            lines.append(f"• {item.product.name} x{item.quantity}")
        lines.append("")
        lines.append(f"💰 Jami: {int(order.total_price):,} so'm".replace(",", " "))

        kb = None
        if order.status == OrderStatus.SERVED:
            kb = rating_kb(order.id)
            lines.append("\n⭐ Buyurtmani baholang:")

        await message.answer("\n".join(lines), reply_markup=kb)


# ---------------- REYTING ----------------
@router.callback_query(RatingCB.filter())
async def rate_order(call: CallbackQuery, callback_data: RatingCB, state: FSMContext) -> None:
    order = await get_order(callback_data.order_id)
    if not order:
        await call.answer("Buyurtma topilmadi", show_alert=True)
        return

    data = await state.get_data()
    user_id = data.get("user_id")

    for item in order.items:
        await add_rating(user_id=user_id, order_id=order.id, product_id=item.product_id, stars=callback_data.stars)

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.message.answer("⭐" * callback_data.stars + "\nRahmat, fikringiz uchun! 🙏")
    await call.answer()


# ---------------- BONUS ----------------
@router.message(F.text == "🎁 Bonus")
async def show_bonus(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    user = await get_user_by_id(user_id)
    balance = float(user.bonus_balance) if user else 0

    text = f"🎁 <b>Bonus balansingiz:</b> {int(balance):,} so'm".replace(",", " ")
    await message.answer(
        text + "\n\nHar bir buyurtmadan bonus to'planadi va keyingi buyurtmalarda chegirma sifatida "
        "ishlatishingiz mumkin. Bonusdan foydalanish uchun ofitsiantga murojaat qiling."
    )


# ---------------- OFITSIANT CHAQIRISH ----------------
@router.callback_query(CallWaiterCB.filter())
async def call_waiter(call: CallbackQuery, callback_data: CallWaiterCB, state: FSMContext) -> None:
    data = await state.get_data()
    table_number = data.get("table_number", "?")

    await notify_waiter_called(call.bot, table_number)
    await call.answer("🔔 Ofitsiant chaqirildi!", show_alert=True)
