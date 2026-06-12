"""Filial (Branch) modeli - bir nechta filial qo'llab-quvvatlash uchun."""
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    tables: Mapped[list["Table"]] = relationship(back_populates="branch")
    admins: Mapped[list["Admin"]] = relationship(back_populates="branch")

    def __repr__(self) -> str:
        return f"<Branch id={self.id} name={self.name!r}>"
