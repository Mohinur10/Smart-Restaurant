"""Savat (Cart) elementi modeli."""
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CartItem(Base):
    """
    Foydalanuvchi savatidagi bitta mahsulot qatori.
    Buyurtma berilganda CartItem -> OrderItem ga ko'chiriladi va o'chiriladi.
    """
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="cart_items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="cart_items")

    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Mahsulotga izoh (piyozsiz, achchiqroq va h.k.)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<CartItem user_id={self.user_id} product_id={self.product_id} qty={self.quantity}>"
