"""Ofitsiant va oshxona xodimlari uchun klaviaturalar."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import Order
from app.models.order import OrderStatus
from app.utils.callbacks import OrderStatusCB


def waiter_main_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📋 Faol buyurtmalar")],
        [KeyboardButton(text="🚪 Chiqish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def kitchen_main_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="👨‍🍳 Navbat")],
        [KeyboardButton(text="🚪 Chiqish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def order_status_kb(order: Order, for_role: str) -> InlineKeyboardMarkup:
    """
    for_role = 'kitchen' -> Tayyorlanmoqda / Tayyor tugmalari
    for_role = 'waiter'  -> Yetkazildi tugmasi (Tayyor bo'lgandan keyin)
    """
    builder = InlineKeyboardBuilder()

    if for_role == "kitchen":
        if order.status == OrderStatus.NEW:
            builder.button(
                text="👨‍🍳 Tayyorlanmoqda",
                callback_data=OrderStatusCB(order_id=order.id, status=OrderStatus.PREPARING.value),
            )
        if order.status == OrderStatus.PREPARING:
            builder.button(
                text="✅ Tayyor",
                callback_data=OrderStatusCB(order_id=order.id, status=OrderStatus.READY.value),
            )

    if for_role == "waiter":
        if order.status == OrderStatus.READY:
            builder.button(
                text="🍽 Yetkazildi",
                callback_data=OrderStatusCB(order_id=order.id, status=OrderStatus.SERVED.value),
            )

    builder.adjust(1)
    return builder.as_markup()
