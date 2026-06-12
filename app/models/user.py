"""Mijoz (User) modeli."""
from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Bonus tizimi
    bonus_balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    language: Mapped[str] = mapped_column(String(5), default="uz")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id}>"
