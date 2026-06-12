"""
Smart Restaurant QR System - bot entry point.
Polling rejimida ishga tushiradi, DB va routerlarni ulaydi.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import config
from app.database import init_db, close_db
from app.services.admin_service import ensure_super_admin

# ---- User handlers ----
from app.handlers.user import start as user_start
from app.handlers.user import menu as user_menu
from app.handlers.user import cart as user_cart
from app.handlers.user import extra as user_extra
from app.handlers.user import reservation as user_reservation

# ---- Admin handlers ----
from app.handlers.admin import auth as admin_auth
from app.handlers.admin import categories as admin_categories
from app.handlers.admin import products as admin_products
from app.handlers.admin import orders as admin_orders
from app.handlers.admin import stats as admin_stats
from app.handlers.admin import staff as admin_staff
from app.handlers.admin import promo as admin_promo
from app.handlers.admin import tables as admin_tables

# ---- Waiter / Kitchen handlers ----
from app.handlers.waiter import orders as waiter_orders
from app.handlers.kitchen import queue as kitchen_queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # --- Auth (eng birinchi, chunki /admin, /staff, "Chiqish" shu yerda) ---
    dp.include_router(admin_auth.router)

    # --- Admin panel ---
    dp.include_router(admin_categories.router)
    dp.include_router(admin_products.router)
    dp.include_router(admin_orders.router)
    dp.include_router(admin_stats.router)
    dp.include_router(admin_staff.router)
    dp.include_router(admin_promo.router)
    dp.include_router(admin_tables.router)

    # --- Ofitsiant / Oshxona ---
    dp.include_router(waiter_orders.router)
    dp.include_router(kitchen_queue.router)

    # --- User (oddiy mijoz) ---
    dp.include_router(user_start.router)
    dp.include_router(user_menu.router)
    dp.include_router(user_cart.router)
    dp.include_router(user_extra.router)
    dp.include_router(user_reservation.router)

    # Baza jadvallarini yaratish
    await init_db()
    logger.info("Database tayyor.")

    # Bosh adminni yaratish (.env dagi ADMIN_USERNAME/ADMIN_PASSWORD)
    await ensure_super_admin(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
    logger.info("Bosh admin tayyor (login: %s).", config.ADMIN_USERNAME)

    # UptimeRobot / Render Web Service uchun oddiy web server
    from aiohttp import web
    import os
    
    async def handle_ping(request):
        return web.Response(text="Bot is alive!")
        
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", config.WEBAPP_PORT))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server ishga tushdi (Port: {port}). UptimeRobot uchun tayyor.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot polling rejimida ishga tushdi.")
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
