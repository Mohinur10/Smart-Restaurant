"""Foydalanuvchi (user) uchun klaviaturalar."""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import Category, Product, CartItem
from app.utils.callbacks import (
    CategoryCB, ProductCB, CartAddCB, CartItemCB,
    FavoriteCB, OrderTypeCB, CallWaiterCB, RatingCB,
)


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Asosiy menyu (reply klaviatura)."""
    kb = [
        [KeyboardButton(text="📋 Menyu"), KeyboardButton(text="🛒 Savat")],
        [KeyboardButton(text="🔍 Qidirish"), KeyboardButton(text="❤️ Saqlanganlar")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="🎁 Bonus")],
        [KeyboardButton(text="📅 Stol band qilish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.display_name, callback_data=CategoryCB(id=cat.id))
    builder.adjust(2)
    return builder.as_markup()


def products_kb(products: list[Product], category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        title = f"{p.name} — {int(p.price):,} so'm".replace(",", " ")
        builder.button(text=title, callback_data=ProductCB(id=p.id))
    builder.button(text="⬅️ Kategoriyalarga qaytish", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


def product_card_kb(product: Product, is_fav: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Savatga qo'shish", callback_data=CartAddCB(product_id=product.id))
    fav_text = "💔 Saqlanganlardan olish" if is_fav else "❤️ Saqlash"
    builder.button(text=fav_text, callback_data=FavoriteCB(action="remove" if is_fav else "add", product_id=product.id))
    builder.button(text="⬅️ Ortga", callback_data=CategoryCB(id=product.category_id))
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(items: list[CartItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        name = item.product.name
        builder.button(text=f"➖", callback_data=CartItemCB(action="dec", item_id=item.id))
        builder.button(text=f"{name} x{item.quantity}", callback_data=CartItemCB(action="noop", item_id=item.id))
        builder.button(text=f"➕", callback_data=CartItemCB(action="inc", item_id=item.id))
        builder.button(text="🗑", callback_data=CartItemCB(action="remove", item_id=item.id))
        builder.button(text="💬", callback_data=CartItemCB(action="comment", item_id=item.id))

    builder.adjust(*([5] * len(items)) if items else [1])

    extra = InlineKeyboardBuilder()
    if items:
        extra.button(text="✅ Buyurtma berish", callback_data="checkout")
        extra.button(text="🗑 Savatni tozalash", callback_data="cart_clear")
    extra.adjust(1)

    builder.attach(extra)
    return builder.as_markup()


def order_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🍽 Shu yerda yeyman", callback_data=OrderTypeCB(value="dine_in"))
    builder.button(text="📦 Olib ketaman", callback_data=OrderTypeCB(value="takeaway"))
    builder.adjust(1)
    return builder.as_markup()


def skip_kb(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ O'tkazib yuborish", callback_data=callback_data)
    return builder.as_markup()


def confirm_order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="order_confirm")
    builder.button(text="❌ Bekor qilish", callback_data="order_cancel")
    builder.adjust(2)
    return builder.as_markup()


def call_waiter_kb(table_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Ofitsiantni chaqirish", callback_data=CallWaiterCB(table_id=table_id))
    return builder.as_markup()


def rating_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text="⭐" * i, callback_data=RatingCB(order_id=order_id, stars=i))
    builder.adjust(1)
    return builder.as_markup()


def payment_method_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Naqd", callback_data="pay_cash")
    builder.button(text="💳 Karta", callback_data="pay_card")
    builder.button(text="📲 Click", callback_data="pay_click")
    builder.button(text="📲 Payme", callback_data="pay_payme")
    builder.adjust(2)
    return builder.as_markup()
