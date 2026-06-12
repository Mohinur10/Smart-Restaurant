"""Ofitsiant, oshxona va userlarga xabar yuborish uchun yordamchi funksiyalar."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.models import Order
from app.models.admin import StaffRole
from app.services.admin_service import get_staff_by_role
from app.keyboards.staff_kb import order_status_kb

logger = logging.getLogger(__name__)


def _format_order_text(order: Order) -> str:
    table_text = f"Stol: <b>{order.table.number}</b>" if order.table else "📦 Olib ketish"
    lines = [f"🔔 <b>Yangi buyurtma #{order.id}</b>", table_text, ""]
    for item in order.items:
        line = f"{item.quantity} x {item.product.name}"
        if item.comment:
            line += f" ({item.comment})"
        lines.append(line)
    if order.comment:
        lines.append("")
        lines.append(f"💬 Izoh: {order.comment}")
    if order.guests_count:
        lines.append(f"👥 Kishi soni: {order.guests_count}")
    lines.append("")
    lines.append(f"💰 Jami: {int(order.total_price):,} so'm".replace(",", " "))
    return "\n".join(lines)


async def _safe_send(bot: Bot, chat_id: int, text: str, **kwargs):
    try:
        return await bot.send_message(chat_id, text, **kwargs)
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.warning("Xabar yuborilmadi (chat_id=%s): %s", chat_id, e)
        return None


async def notify_kitchen_new_order(bot: Bot, order: Order) -> None:
    """Yangi buyurtma haqida oshxona xodimlariga xabar."""
    kitchen_staff = await get_staff_by_role(StaffRole.KITCHEN)
    text = _format_order_text(order)
    kb = order_status_kb(order, for_role="kitchen")
    for staff in kitchen_staff:
        if staff.telegram_id:
            await _safe_send(bot, staff.telegram_id, text, reply_markup=kb)


async def notify_waiter_new_order(bot: Bot, order: Order) -> None:
    """Yangi buyurtma haqida ofitsiantlarga xabar."""
    waiters = await get_staff_by_role(StaffRole.WAITER)
    text = _format_order_text(order)
    for staff in waiters:
        if staff.telegram_id:
            await _safe_send(bot, staff.telegram_id, text)


async def notify_waiter_order_ready(bot: Bot, order: Order) -> None:
    """Buyurtma tayyor bo'lganda ofitsiantlarga xabar (yetkazish uchun)."""
    waiters = await get_staff_by_role(StaffRole.WAITER)
    table_text = f"Stol {order.table.number}" if order.table else f"Buyurtma #{order.id}"
    text = f"✅ <b>Tayyor bo'ldi!</b>\n{table_text} — Buyurtma #{order.id} ni yetkazing."
    kb = order_status_kb(order, for_role="waiter")
    for staff in waiters:
        if staff.telegram_id:
            await _safe_send(bot, staff.telegram_id, text, reply_markup=kb)


async def notify_user_order_ready(bot: Bot, order: Order) -> None:
    """Buyurtma tayyor bo'lganda mijozga xabar."""
    if order.user and order.user.telegram_id:
        await _safe_send(bot, order.user.telegram_id, "✅ <b>Buyurtmangiz tayyor!</b>\nYoqimli ishtaha 😊")


async def notify_waiter_called(bot: Bot, table_number: int) -> None:
    """Mijoz ofitsiant chaqirganda xabar."""
    waiters = await get_staff_by_role(StaffRole.WAITER)
    text = f"🔔 <b>{table_number}-stol</b> ofitsiantni chaqirmoqda!"
    for staff in waiters:
        if staff.telegram_id:
            await _safe_send(bot, staff.telegram_id, text)
