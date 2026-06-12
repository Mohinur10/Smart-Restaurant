"""Admin, Ofitsiant, Oshxona xodimlari modeli."""
import enum

from sqlalchemy import String, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StaffRole(str, enum.Enum):
    ADMIN = "admin"
    WAITER = "waiter"
    KITCHEN = "kitchen"


class Admin(Base):
    """
    Tizim xodimlari: Admin, Ofitsiant, Oshxona.
    Telegram ID orqali aniqlanadi, role bo'yicha huquqlar farqlanadi.
    """
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole), default=StaffRole.ADMIN)

    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    branch: Mapped["Branch"] = relationship(back_populates="admins")

    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<Admin id={self.id} username={self.username!r} role={self.role}>"
