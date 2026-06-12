"""Oshxona: buyurtmalar navbati va holat o'zgartirish."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.services.order_service import get_active_orders, update_order_status
from app.services.notify_service import notify_waiter_order_ready, notify_user_order_ready
from app.models.order import OrderStatus
from app.keyboards.staff_kb import order_status_kb
from app.utils.callbacks import OrderStatusCB
from app.utils.filters import IsKitchen

router = Router(name="kitchen_queue")
router.message.filter(IsKitchen())
router.callback_query.filter(IsKitchen())


def _order_text(order) -> str:
    table_text = f"Stol {order.table.number}" if order.table else "📦 Olib ketish"
    lines = [f"<b>Buyurtma #{order.id}</b> — {table_text}", ""]
    for item in order.items:
        line = f"{item.quantity} x {item.product.name} ({item.product.cook_time_minutes} daq.)"
        if item.comment:
            line += f"\n   💬 {item.comment}"
        lines.append(line)
    return "\n".join(lines)


@router.message(F.text == "👨‍🍳 Navbat")
async def show_queue(message: Message) -> None:
    orders = await get_active_orders()
    queue = [o for o in orders if o.status in (OrderStatus.NEW, OrderStatus.PREPARING)]

    if not queue:
        await message.answer("✅ Navbat bo'sh — barcha buyurtmalar tayyor!")
        return

    for order in queue:
        await message.answer(_order_text(order), reply_markup=order_status_kb(order, for_role="kitchen"))


@router.callback_query(OrderStatusCB.filter(F.status == OrderStatus.PREPARING.value))
async def mark_preparing(call: CallbackQuery, callback_data: OrderStatusCB) -> None:
    order = await update_order_status(callback_data.order_id, OrderStatus.PREPARING)
    await call.message.edit_text(_order_text(order), reply_markup=order_status_kb(order, for_role="kitchen"))
    await call.answer("👨‍🍳 Tayyorlanmoqda")


@router.callback_query(OrderStatusCB.filter(F.status == OrderStatus.READY.value))
async def mark_ready(call: CallbackQuery, callback_data: OrderStatusCB) -> None:
    order = await update_order_status(callback_data.order_id, OrderStatus.READY)

    await call.message.edit_text(_order_text(order) + "\n\n✅ <b>Tayyor!</b>")
    await call.answer("✅ Tayyor deb belgilandi")

    await notify_user_order_ready(call.bot, order)
    await notify_waiter_order_ready(call.bot, order)
