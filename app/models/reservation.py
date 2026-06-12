"""Stol rezervatsiyasi (Reservation) modeli."""
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Integer, String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    table: Mapped["Table"] = relationship(back_populates="reservations")

    guests_count: Mapped[int] = mapped_column(Integer, default=1)
    reserved_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # rezerv qilingan vaqt

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), default=ReservationStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Reservation table_id={self.table_id} at={self.reserved_at}>"
