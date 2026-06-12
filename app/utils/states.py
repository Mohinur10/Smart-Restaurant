"""Barcha bo'limlar uchun FSM (Finite State Machine) holatlari."""
from aiogram.fsm.state import State, StatesGroup


# ---------------- ADMIN ----------------
class AdminAuth(StatesGroup):
    waiting_username = State()
    waiting_password = State()


class StaffAuth(StatesGroup):
    waiting_username = State()
    waiting_password = State()


class CategoryForm(StatesGroup):
    waiting_name = State()
    waiting_emoji = State()
    editing_name = State()


class ProductForm(StatesGroup):
    waiting_category = State()
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_image = State()
    waiting_cook_time = State()
    waiting_quantity = State()
    waiting_code = State()
    # Tahrirlash uchun
    editing_field = State()
    editing_value = State()


class StaffForm(StatesGroup):
    waiting_full_name = State()
    waiting_username = State()
    waiting_password = State()


class PromoForm(StatesGroup):
    waiting_code = State()
    waiting_discount = State()
    waiting_limit = State()


# ---------------- USER ----------------
class OrderForm(StatesGroup):
    choosing_type = State()
    entering_guests = State()
    entering_comment = State()
    confirming = State()


class CartItemComment(StatesGroup):
    waiting_comment = State()


class SearchProduct(StatesGroup):
    waiting_query = State()


class ReservationForm(StatesGroup):
    choosing_table = State()
    entering_datetime = State()
    entering_guests = State()
    entering_phone = State()


class RatingForm(StatesGroup):
    waiting_stars = State()
    waiting_comment = State()
