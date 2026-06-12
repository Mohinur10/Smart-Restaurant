"""Restoran stoli (Table) modeli - har bir QR kod shu jadvalga bog'lanadi."""
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)  # Stol raqami (masalan 7)

    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    branch: Mapped["Branch"] = relationship(back_populates="tables")

    # QR kod orqali kelganda ishlatiladigan noyob token (deep-link parametri)
    qr_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    orders: Mapped[list["Order"]] = relationship(back_populates="table")
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="table")

    def __repr__(self) -> str:
        return f"<Table id={self.id} number={self.number}>"
