"""Mahsulot (taom) modeli."""
from sqlalchemy import String, Numeric, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # Tarkibi / tavsif
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Telegram file_id - rasmni Telegram serverida saqlash (pullik storage YO'Q)
    image_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tayyor bo'lish vaqti (daqiqalarda)
    cook_time_minutes: Mapped[int] = mapped_column(Integer, default=10)

    # Mavjud miqdor / sklad
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    # Mahsulot kodi (qidirish uchun)
    product_code: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)

    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")

    # Relationships
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    @property
    def avg_rating(self) -> float:
        """O'rtacha reyting (agar ratings yuklangan bo'lsa)."""
        if not self.ratings:
            return 0.0
        return round(sum(r.stars for r in self.ratings) / len(self.ratings), 1)

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"
