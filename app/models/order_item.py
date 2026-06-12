"""Buyurtma tarkibidagi bitta mahsulot (OrderItem) modeli."""
import enum

from sqlalchemy import Integer, ForeignKey, String, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ItemStatus(str, enum.Enum):
    """Har bir taom alohida oshxona navbatida bo'lishi mumkin."""
    NEW = "new"
    PREPARING = "preparing"
    READY = "ready"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["Order"] = relationship(back_populates="items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="order_items")

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Buyurtma berilgan paytdagi narx (keyinchalik narx o'zgarsa ham tarix saqlanadi)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ItemStatus] = mapped_column(Enum(ItemStatus), default=ItemStatus.NEW)

    @property
    def subtotal(self) -> float:
        return float(self.price) * self.quantity

    def __repr__(self) -> str:
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id} qty={self.quantity}>"
