"""Aksiya / Promokod modeli."""
from datetime import datetime

from sqlalchemy import String, Numeric, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    # Chegirma foizda (masalan 10 => 10%)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)

    # Necha marta ishlatilishi mumkin (None = cheksiz)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def __repr__(self) -> str:
        return f"<PromoCode code={self.code!r} discount={self.discount_percent}%>"
