"""Savat ko'rish, tahrirlash va buyurtma berish (checkout) oqimi."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.user_kb import (
    cart_kb, order_type_kb, skip_kb, confirm_order_kb,
    payment_method_kb, call_waiter_kb, main_menu_kb,
)
from app.services.cart_service import (
    get_cart_items, get_cart_total, change_quantity,
    remove_item, clear_cart, set_item_comment, get_cart_item,
)
from app.services.order_service import create_order_from_cart
from app.services.promo_service import get_promo_by_code
from app.services.notify_service import notify_kitchen_new_order, notify_waiter_new_order
from app.models.order import OrderType, PaymentMethod
from app.utils.callbacks import CartItemCB, OrderTypeCB
from app.utils.states import OrderForm, CartItemComment

router = Router(name="user_cart")


def _cart_text(items, total: float) -> str:
    if not items:
        return "🛒 Savatingiz bo'sh.\n\nMenyudan mahsulot tanlang!"
    lines = ["🛒 <b>Savat:</b>", ""]
    for item in items:
        subtotal = float(item.product.price) * item.quantity
        line = f"• {item.product.name} x{item.quantity} = {int(subtotal):,} so'm".replace(",", " ")
        if item.comment:
            line += f"\n   💬 {item.comment}"
        lines.append(line)
    lines.append("")
    lines.append(f"💰 <b>Jami: {int(total):,} so'm</b>".replace(",", " "))
    return "\n".join(lines)


@router.message(F.text == "🛒 Savat")
async def show_cart(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    total = await get_cart_total(user_id)
    await message.answer(_cart_text(items, total), reply_markup=cart_kb(items))


@router.callback_query(CartItemCB.filter(F.action == "noop"))
async def noop(call: CallbackQuery) -> None:
    await call.answer()


@router.callback_query(CartItemCB.filter(F.action.in_({"inc", "dec"})))
async def change_item_qty(call: CallbackQuery, callback_data: CartItemCB, state: FSMContext) -> None:
    delta = 1 if callback_data.action == "inc" else -1
    await change_quantity(callback_data.item_id, delta)

    data = await state.get_data()
    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    total = await get_cart_total(user_id)

    try:
        await call.message.edit_text(_cart_text(items, total), reply_markup=cart_kb(items))
    except Exception:
        pass
    await call.answer()


@router.callback_query(CartItemCB.filter(F.action == "remove"))
async def remove_cart_item(call: CallbackQuery, callback_data: CartItemCB, state: FSMContext) -> None:
    await remove_item(callback_data.item_id)

    data = await state.get_data()
    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    total = await get_cart_total(user_id)

    try:
        await call.message.edit_text(_cart_text(items, total), reply_markup=cart_kb(items))
    except Exception:
        pass
    await call.answer("🗑 O'chirildi")


@router.callback_query(F.data == "cart_clear")
async def cart_clear(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    await clear_cart(user_id)
    try:
        await call.message.edit_text(_cart_text([], 0), reply_markup=cart_kb([]))
    except Exception:
        pass
    await call.answer("🗑 Savat tozalandi")


@router.callback_query(CartItemCB.filter(F.action == "comment"))
async def ask_item_comment(call: CallbackQuery, callback_data: CartItemCB, state: FSMContext) -> None:
    await state.update_data(comment_item_id=callback_data.item_id)
    await state.set_state(CartItemComment.waiting_comment)
    await call.message.answer(
        "💬 Mahsulot uchun izoh kiriting (masalan: <i>piyozsiz, achchiqroq</i>):"
    )
    await call.answer()


@router.message(CartItemComment.waiting_comment)
async def save_item_comment(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    item_id = data.get("comment_item_id")
    await set_item_comment(item_id, message.text.strip())
    await state.set_state(None)

    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    total = await get_cart_total(user_id)
    await message.answer("✅ Izoh saqlandi.")
    await message.answer(_cart_text(items, total), reply_markup=cart_kb(items))


# ---------------- CHECKOUT OQIMI ----------------
@router.callback_query(F.data == "checkout")
async def start_checkout(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    if not items:
        await call.answer("Savat bo'sh", show_alert=True)
        return

    await state.set_state(OrderForm.choosing_type)
    await call.message.answer("Buyurtma turini tanlang:", reply_markup=order_type_kb())
    await call.answer()


@router.callback_query(OrderForm.choosing_type, OrderTypeCB.filter())
async def choose_order_type(call: CallbackQuery, callback_data: OrderTypeCB, state: FSMContext) -> None:
    await state.update_data(order_type=callback_data.value)

    if callback_data.value == "dine_in":
        await state.set_state(OrderForm.entering_guests)
        await call.message.answer("👥 Necha kishi bo'lasiz? (raqam kiriting)")
    else:
        await state.update_data(guests_count=None)
        await state.set_state(OrderForm.entering_comment)
        await call.message.answer(
            "💬 Buyurtmaga umumiy izoh qoldirmoqchimisiz? (yozing yoki o'tkazib yuboring)",
            reply_markup=skip_kb("skip_comment"),
        )
    await call.answer()


@router.message(OrderForm.entering_guests)
async def enter_guests(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("⚠️ Iltimos, musbat raqam kiriting.")
        return
    await state.update_data(guests_count=int(text))
    await state.set_state(OrderForm.entering_comment)
    await message.answer(
        "💬 Buyurtmaga umumiy izoh qoldirmoqchimisiz? (yozing yoki o'tkazib yuboring)",
        reply_markup=skip_kb("skip_comment"),
    )


@router.callback_query(OrderForm.entering_comment, F.data == "skip_comment")
async def skip_comment(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(comment=None)
    await _show_order_summary(call.message, state)
    await call.answer()


@router.message(OrderForm.entering_comment)
async def enter_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=message.text.strip())
    await _show_order_summary(message, state)


async def _show_order_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")
    items = await get_cart_items(user_id)
    total = await get_cart_total(user_id)

    order_type_text = "🍽 Shu yerda yeyman" if data.get("order_type") == "dine_in" else "📦 Olib ketaman"
    lines = [_cart_text(items, total), "", f"📌 Tur: {order_type_text}"]
    if data.get("guests_count"):
        lines.append(f"👥 Kishi soni: {data['guests_count']}")
    if data.get("comment"):
        lines.append(f"💬 Izoh: {data['comment']}")

    await state.set_state(OrderForm.confirming)
    await message.answer("\n".join(lines), reply_markup=confirm_order_kb())


@router.callback_query(OrderForm.confirming, F.data == "order_cancel")
async def cancel_order(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await call.message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())
    await call.answer()


@router.callback_query(OrderForm.confirming, F.data == "order_confirm")
async def confirm_order(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("💳 To'lov turini tanlang:", reply_markup=payment_method_kb())
    await call.answer()


@router.callback_query(OrderForm.confirming, F.data.startswith("pay_"))
async def finalize_order(call: CallbackQuery, state: FSMContext) -> None:
    method_map = {
        "pay_cash": PaymentMethod.CASH,
        "pay_card": PaymentMethod.CARD,
        "pay_click": PaymentMethod.CLICK,
        "pay_payme": PaymentMethod.PAYME,
    }
    method = method_map.get(call.data)

    data = await state.get_data()
    user_id = data.get("user_id")
    table_id = data.get("table_id")
    order_type = OrderType(data.get("order_type", "dine_in"))
    guests_count = data.get("guests_count")
    comment = data.get("comment")

    order = await create_order_from_cart(
        user_id=user_id,
        table_id=table_id,
        order_type=order_type,
        guests_count=guests_count,
        comment=comment,
    )

    if not order:
        await call.message.answer("⚠️ Savat bo'sh, buyurtma yaratilmadi.")
        await state.set_state(None)
        await call.answer()
        return

    # To'lov usulini saqlash
    from app.database import get_session
    async with get_session() as session:
        db_order = await session.get(type(order), order.id)
        db_order.payment_method = method
        await session.commit()

    # Oshxona va ofitsiantlarga xabar
    await notify_kitchen_new_order(call.bot, order)
    await notify_waiter_new_order(call.bot, order)

    total_minutes = max((item.product.cook_time_minutes for item in order.items), default=10)

    text = (
        f"✅ <b>Buyurtmangiz qabul qilindi!</b> (#{order.id})\n\n"
        f"⏱ Taxminan <b>{total_minutes} daqiqa</b>da tayyor bo'ladi.\n"
        f"Yoqimli ishtaha! 😊"
    )

    kb = None
    if table_id:
        kb = call_waiter_kb(table_id)

    await call.message.answer(text, reply_markup=main_menu_kb())
    if kb:
        await call.message.answer("Yordam kerak bo'lsa:", reply_markup=kb)

    await state.set_state(None)
    await call.answer()
