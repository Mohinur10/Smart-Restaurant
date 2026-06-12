"""Admin: Statistika (bugungi kun)."""
from aiogram import Router, F
from aiogram.types import Message

from app.services.order_service import get_today_stats
from app.utils.filters import IsAdmin

router = Router(name="admin_stats")
router.message.filter(IsAdmin())


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    stats = await get_today_stats()
    revenue_text = f"{int(stats['revenue']):,} so'm".replace(",", " ")

    text = (
        "📊 <b>Bugungi statistika:</b>\n\n"
        f"🧾 Buyurtmalar soni: <b>{stats['orders_count']}</b>\n"
        f"💰 Daromad: <b>{revenue_text}</b>\n"
        f"🔥 Eng ko'p sotilgan: <b>{stats['top_product']}</b>\n"
        f"⏰ Eng band vaqt: <b>{stats['busy_hour']}</b>"
    )
    await message.answer(text)
