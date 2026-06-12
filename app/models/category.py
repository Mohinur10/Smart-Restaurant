"""Mahsulot kategoriyasi modeli (🍔 Ovqatlar, 🍕 Fast food va h.k.)."""
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Tartiblash uchun (menyuda ko'rsatish tartibi)
    position: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")

    @property
    def display_name(self) -> str:
        """Emoji + nom (masalan: '🍔 Ovqatlar')."""
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"
