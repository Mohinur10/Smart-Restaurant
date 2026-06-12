"""Admin panel uchun klaviaturalar."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import Category, Product, Order, PromoCode
from app.models.admin import Admin
from app.utils.callbacks import (
    AdminCatCB, AdminProdCB, AdminOrderCB, AdminStaffCB, AdminPromoCB,
)


def admin_main_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📂 Kategoriyalar"), KeyboardButton(text="📦 Mahsulotlar")],
        [KeyboardButton(text="🚚 Buyurtmalar"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🎁 Aksiyalar"), KeyboardButton(text="👥 Xodimlar")],
        [KeyboardButton(text="🪑 Stollar"), KeyboardButton(text="🚪 Chiqish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ---------------- KATEGORIYALAR ----------------
def admin_categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        status = "✅" if cat.is_active else "🚫"
        builder.button(text=f"{status} {cat.display_name}", callback_data=AdminCatCB(action="view", id=cat.id))
    builder.button(text="➕ Yangi kategoriya", callback_data="acat_new")
    builder.adjust(1)
    return builder.as_markup()


def admin_category_detail_kb(category: Category) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Nomini o'zgartirish", callback_data=AdminCatCB(action="edit", id=category.id))
    toggle_text = "🚫 Faolsizlantirish" if category.is_active else "✅ Faollashtirish"
    builder.button(text=toggle_text, callback_data=AdminCatCB(action="toggle", id=category.id))
    builder.button(text="🗑 O'chirish", callback_data=AdminCatCB(action="delete", id=category.id))
    builder.button(text="⬅️ Ortga", callback_data="acat_list")
    builder.adjust(1)
    return builder.as_markup()


# ---------------- MAHSULOTLAR ----------------
def admin_categories_for_product_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.display_name, callback_data=AdminCatCB(action="pick", id=cat.id))
    builder.adjust(2)
    return builder.as_markup()


def admin_products_kb(products: list[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        status = "✅" if p.is_available else "❌"
        builder.button(text=f"{status} {p.name}", callback_data=AdminProdCB(action="view", id=p.id))
    builder.button(text="➕ Yangi mahsulot", callback_data="aprod_new")
    builder.adjust(1)
    return builder.as_markup()


def admin_product_detail_kb(product: Product) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = [
        ("✏️ Nomi", "name"),
        ("📝 Tavsif", "description"),
        ("💰 Narxi", "price"),
        ("🖼 Rasm", "image_file_id"),
        ("⏱ Tayyorlanish vaqti", "cook_time_minutes"),
        ("🔢 Soni", "quantity"),
        ("🏷 Kodi", "product_code"),
    ]
    for label, field in fields:
        builder.button(text=label, callback_data=AdminProdCB(action="edit_field", id=product.id, field=field))

    toggle_text = "❌ Mavjud emas qilish" if product.is_available else "✅ Mavjud qilish"
    builder.button(text=toggle_text, callback_data=AdminProdCB(action="toggle", id=product.id))
    builder.button(text="🗑 O'chirish", callback_data=AdminProdCB(action="delete", id=product.id))
    builder.button(text="⬅️ Ortga", callback_data="aprod_list")
    builder.adjust(2)
    return builder.as_markup()


# ---------------- BUYURTMALAR ----------------
def admin_order_detail_kb(order: Order) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Buyurtmalar ro'yxati", callback_data="aord_list")
    return builder.as_markup()


# ---------------- XODIMLAR ----------------
def admin_staff_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧑‍💼 Ofitsiant qo'shish", callback_data="astaff_add_waiter")
    builder.button(text="👨‍🍳 Oshpaz qo'shish", callback_data="astaff_add_kitchen")
    builder.button(text="📋 Xodimlar ro'yxati", callback_data="astaff_list")
    builder.adjust(1)
    return builder.as_markup()


def admin_staff_list_kb(staff_list: list[Admin]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    role_emoji = {"admin": "👑", "waiter": "🧑‍💼", "kitchen": "👨‍🍳"}
    for s in staff_list:
        status = "✅" if s.is_active else "🚫"
        role_val = s.role.value if hasattr(s.role, "value") else s.role
        emoji = role_emoji.get(role_val, "👤")
        builder.button(
            text=f"{status} {emoji} {s.full_name} ({s.username})",
            callback_data=AdminStaffCB(action="view", id=s.id),
        )
    builder.adjust(1)
    return builder.as_markup()


def admin_staff_detail_kb(staff: Admin) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_text = "🚫 Bloklash" if staff.is_active else "✅ Aktivlashtirish"
    builder.button(text=toggle_text, callback_data=AdminStaffCB(action="toggle", id=staff.id))
    builder.button(text="🗑 O'chirish", callback_data=AdminStaffCB(action="delete", id=staff.id))
    builder.button(text="⬅️ Ortga", callback_data="astaff_list")
    builder.adjust(1)
    return builder.as_markup()


# ---------------- AKSIYALAR / PROMOKOD ----------------
def admin_promo_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Yangi promokod", callback_data="aprm_new")
    builder.adjust(1)
    return builder.as_markup()


def admin_promo_list_kb(promos: list[PromoCode]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in promos:
        status = "✅" if p.is_active else "🚫"
        builder.button(
            text=f"{status} {p.code} (-{p.discount_percent}%)",
            callback_data=AdminPromoCB(action="toggle", id=p.id),
        )
        builder.button(text=f"🗑 {p.code}", callback_data=AdminPromoCB(action="delete", id=p.id))
    builder.adjust(2)
    return builder.as_markup()


# ---------------- STOLLAR ----------------
def admin_tables_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Yangi stol qo'shish", callback_data="atable_new")
    builder.adjust(1)
    return builder.as_markup()
