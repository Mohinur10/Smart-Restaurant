"""Admin: Buyurtmalarni ko'rish."""
from aiogram import Router, F
from aiogram.types import Message

from app.services.order_service import get_active_orders
from app.models.order import OrderStatus
from app.utils.filters import IsAdmin

router = Router(name="admin_orders")
router.message.filter(IsAdmin())

STATUS_TEXT = {
    OrderStatus.NEW: "🆕 Yangi",
    OrderStatus.PREPARING: "👨‍🍳 Tayyorlanmoqda",
    OrderStatus.READY: "✅ Tayyor",
    OrderStatus.SERVED: "🍽 Yetkazildi",
    OrderStatus.CANCELLED: "❌ Bekor qilindi",
}


@router.message(F.text == "🚚 Buyurtmalar")
async def list_orders(message: Message) -> None:
    orders = await get_active_orders()
    if not orders:
        await message.answer("😔 Hozircha faol buyurtmalar yo'q.")
        return

    for order in orders:
        table_text = f"Stol {order.table.number}" if order.table else "📦 Olib ketish"
        lines = [
            f"<b>Buyurtma #{order.id}</b> — {table_text}",
            f"Holat: {STATUS_TEXT.get(order.status, order.status)}",
            "",
        ]
        for item in order.items:
            lines.append(f"• {item.product.name} x{item.quantity}")
        lines.append("")
        lines.append(f"💰 Jami: {int(order.total_price):,} so'm".replace(",", " "))
        await message.answer("\n".join(lines))
