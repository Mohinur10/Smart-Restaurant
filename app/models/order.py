"""Buyurtma (Order) modeli."""
import enum
from datetime import datetime

from sqlalchemy import String, ForeignKey, Numeric, DateTime, func, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    NEW = "new"                    # Yangi
    PREPARING = "preparing"        # Tayyorlanmoqda
    READY = "ready"                 # Tayyor
    SERVED = "served"               # Yetkazildi / berildi
    CANCELLED = "cancelled"          # Bekor qilindi


class OrderType(str, enum.Enum):
    DINE_IN = "dine_in"     # Shu yerda yeyman
    TAKEAWAY = "takeaway"   # Olib ketaman


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    CLICK = "click"
    PAYME = "payme"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="orders")

    table_id: Mapped[int | None] = mapped_column(ForeignKey("tables.id"), nullable=True)
    table: Mapped["Table"] = relationship(back_populates="orders")

    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType), default=OrderType.DINE_IN)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW, index=True)

    # Necha kishi (shu yerda yeyman bo'lsa)
    guests_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Umumiy izoh (butun buyurtma uchun)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    total_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    payment_method: Mapped[PaymentMethod | None] = mapped_column(Enum(PaymentMethod), nullable=True)

    # Promo kod ishlatilgan bo'lsa
    promo_code_id: Mapped[int | None] = mapped_column(ForeignKey("promo_codes.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    ready_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payment: Mapped["Payment"] = relationship(back_populates="order", uselist=False, cascade="all, delete-orphan")
    rating: Mapped["Rating"] = relationship(back_populates="order", uselist=False)

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status} total={self.total_price}>"
