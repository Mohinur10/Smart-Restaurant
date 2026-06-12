"""Ofitsiant: faol buyurtmalarni ko'rish va yetkazilgan deb belgilash."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.services.order_service import get_active_orders, update_order_status
from app.models.order import OrderStatus
from app.keyboards.staff_kb import order_status_kb
from app.utils.callbacks import OrderStatusCB
from app.utils.filters import IsWaiter

router = Router(name="waiter_orders")
router.message.filter(IsWaiter())
router.callback_query.filter(IsWaiter())

STATUS_TEXT = {
    OrderStatus.NEW: "🆕 Yangi",
    OrderStatus.PREPARING: "👨‍🍳 Tayyorlanmoqda",
    OrderStatus.READY: "✅ Tayyor",
    OrderStatus.SERVED: "🍽 Yetkazildi",
}


def _order_text(order) -> str:
    table_text = f"Stol {order.table.number}" if order.table else "📦 Olib ketish"
    lines = [
        f"<b>Buyurtma #{order.id}</b> — {table_text}",
        f"Holat: {STATUS_TEXT.get(order.status, order.status)}",
        "",
    ]
    for item in order.items:
        lines.append(f"• {item.product.name} x{item.quantity}")
    return "\n".join(lines)


@router.message(F.text == "📋 Faol buyurtmalar")
async def list_active(message: Message) -> None:
    orders = await get_active_orders()
    if not orders:
        await message.answer("😔 Hozircha faol buyurtmalar yo'q.")
        return

    for order in orders:
        await message.answer(_order_text(order), reply_markup=order_status_kb(order, for_role="waiter"))


@router.callback_query(OrderStatusCB.filter(F.status == OrderStatus.SERVED.value))
async def mark_served(call: CallbackQuery, callback_data: OrderStatusCB) -> None:
    order = await update_order_status(callback_data.order_id, OrderStatus.SERVED)
    await call.message.edit_text(_order_text(order))
    await call.answer("🍽 Yetkazildi deb belgilandi")
