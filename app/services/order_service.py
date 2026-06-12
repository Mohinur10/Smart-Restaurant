"""Buyurtma (Order) bilan bog'liq operatsiyalar."""
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Order, OrderItem, OrderStatus, OrderType, CartItem, Product, PromoCode
from app.services.cart_service import get_cart_items, clear_cart


async def create_order_from_cart(
    user_id: int,
    table_id: int | None,
    order_type: OrderType,
    guests_count: int | None = None,
    comment: str | None = None,
    promo_code: PromoCode | None = None,
) -> Order | None:
    """Foydalanuvchi savatidagi mahsulotlardan yangi buyurtma yaratadi."""
    cart_items = await get_cart_items(user_id)
    if not cart_items:
        return None

    async with get_session() as session:
        total = sum(float(item.product.price) * item.quantity for item in cart_items)

        discount = 0.0
        promo_id = None
        if promo_code and promo_code.is_valid():
            discount = round(total * promo_code.discount_percent / 100, 2)
            promo_id = promo_code.id

        order = Order(
            user_id=user_id,
            table_id=table_id,
            order_type=order_type,
            status=OrderStatus.NEW,
            guests_count=guests_count,
            comment=comment,
            total_price=total - discount,
            discount=discount,
            promo_code_id=promo_id,
        )
        session.add(order)
        await session.flush()  # order.id ni olish uchun

        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                comment=cart_item.comment,
            )
            session.add(order_item)

        if promo_code and promo_id:
            promo = await session.get(PromoCode, promo_id)
            if promo:
                promo.used_count += 1

        await session.commit()
        await session.refresh(order)

    await clear_cart(user_id)
    return await get_order(order.id)


async def get_order(order_id: int) -> Order | None:
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.table),
                selectinload(Order.user),
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()


async def get_active_orders() -> list[Order]:
    """Yangi va tayyorlanayotgan buyurtmalar (ofitsiant/oshxona uchun)."""
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.table))
            .where(Order.status.in_([OrderStatus.NEW, OrderStatus.PREPARING, OrderStatus.READY]))
            .order_by(Order.created_at)
        )
        return list(result.scalars().all())


async def update_order_status(order_id: int, status: OrderStatus) -> Order | None:
    async with get_session() as session:
        order = await session.get(Order, order_id)
        if not order:
            return None
        order.status = status
        if status == OrderStatus.READY:
            order.ready_at = datetime.utcnow()
        await session.commit()
    return await get_order(order_id)


async def get_user_orders(user_id: int, limit: int = 10) -> list[Order]:
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# ---------------- STATISTIKA ----------------
async def get_today_stats() -> dict:
    """Bugungi kun statistikasi: buyurtmalar soni, daromad, top mahsulot, band vaqt."""
    async with get_session() as session:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Buyurtmalar soni va daromad (bekor qilinmaganlar)
        result = await session.execute(
            select(func.count(Order.id), func.coalesce(func.sum(Order.total_price), 0))
            .where(Order.created_at >= today_start, Order.status != OrderStatus.CANCELLED)
        )
        orders_count, revenue = result.one()

        # Eng ko'p sotilgan mahsulot
        result = await session.execute(
            select(Product.name, func.sum(OrderItem.quantity).label("total_qty"))
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(Order.created_at >= today_start, Order.status != OrderStatus.CANCELLED)
            .group_by(Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(1)
        )
        top_product_row = result.first()
        top_product = top_product_row[0] if top_product_row else "—"

        # Eng band vaqt (soat bo'yicha)
        result = await session.execute(
            select(func.extract("hour", Order.created_at).label("hour"), func.count(Order.id))
            .where(Order.created_at >= today_start)
            .group_by("hour")
            .order_by(func.count(Order.id).desc())
            .limit(1)
        )
        busy_hour_row = result.first()
        busy_hour = f"{int(busy_hour_row[0]):02d}:00" if busy_hour_row else "—"

        return {
            "orders_count": orders_count or 0,
            "revenue": float(revenue or 0),
            "top_product": top_product,
            "busy_hour": busy_hour,
        }
