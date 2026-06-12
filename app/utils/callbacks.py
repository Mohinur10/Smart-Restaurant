"""Inline tugmalar uchun CallbackData factory'lar (aiogram 3)."""
from aiogram.filters.callback_data import CallbackData


class CategoryCB(CallbackData, prefix="cat"):
    id: int


class ProductCB(CallbackData, prefix="prod"):
    id: int


class CartAddCB(CallbackData, prefix="cadd"):
    product_id: int


class CartItemCB(CallbackData, prefix="citem"):
    action: str  # inc | dec | remove | comment
    item_id: int


class FavoriteCB(CallbackData, prefix="fav"):
    action: str  # add | remove
    product_id: int


class OrderTypeCB(CallbackData, prefix="otype"):
    value: str  # dine_in | takeaway


class OrderStatusCB(CallbackData, prefix="ost"):
    order_id: int
    status: str


class CallWaiterCB(CallbackData, prefix="callw"):
    table_id: int


# ---------------- ADMIN ----------------
class AdminCatCB(CallbackData, prefix="acat"):
    action: str  # view | edit | delete | toggle
    id: int


class AdminProdCB(CallbackData, prefix="aprod"):
    action: str  # view | edit | delete | toggle | edit_field
    id: int
    field: str = ""


class AdminOrderCB(CallbackData, prefix="aord"):
    action: str  # view | status
    order_id: int
    status: str = ""


class AdminStaffCB(CallbackData, prefix="astaff"):
    action: str  # view | delete | toggle
    id: int


class AdminPromoCB(CallbackData, prefix="aprm"):
    action: str  # toggle | delete
    id: int


class RatingCB(CallbackData, prefix="rate"):
    order_id: int
    stars: int


class PaginationCB(CallbackData, prefix="pg"):
    target: str
    page: int
