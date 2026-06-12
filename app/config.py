"""
Bot konfiguratsiyasi.
Barcha maxfiy va muhim sozlamalar .env faylidan o'qiladi.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(f"Environment variable '{key}' o'rnatilmagan! .env faylini tekshiring.")
    return value


@dataclass(frozen=True)
class Config:
    # --- Telegram ---
    BOT_TOKEN: str = field(default_factory=lambda: _get_env("BOT_TOKEN", required=True))

    # --- Database ---
    DATABASE_URL: str = field(
        default_factory=lambda: _get_env("DATABASE_URL", required=True)
        .replace("postgresql://", "postgresql+asyncpg://")
        .replace("sslmode=require", "ssl=require")
        .replace("&channel_binding=require", "")
        .replace("?channel_binding=require", "?")
    )

    # --- Admin ---
    ADMIN_USERNAME: str = field(default_factory=lambda: _get_env("ADMIN_USERNAME", "admin"))
    ADMIN_PASSWORD: str = field(default_factory=lambda: _get_env("ADMIN_PASSWORD", required=True))

    # --- Security ---
    SECRET_KEY: str = field(default_factory=lambda: _get_env("SECRET_KEY", required=True))

    # --- Deploy / Webhook ---
    USE_WEBHOOK: bool = field(default_factory=lambda: _get_env("USE_WEBHOOK", "False").lower() == "true")
    WEBHOOK_HOST: str = field(default_factory=lambda: _get_env("WEBHOOK_HOST", ""))
    WEBHOOK_PATH: str = field(default_factory=lambda: _get_env("WEBHOOK_PATH", "/webhook"))
    WEBAPP_HOST: str = field(default_factory=lambda: _get_env("WEBAPP_HOST", "0.0.0.0"))
    WEBAPP_PORT: int = field(default_factory=lambda: int(_get_env("WEBAPP_PORT", "8080")))

    # --- Guruh ID lar (xabar yuborish uchun) ---
    WAITER_GROUP_ID: int | None = field(
        default_factory=lambda: int(v) if (v := _get_env("WAITER_GROUP_ID", "")) else None
    )
    KITCHEN_GROUP_ID: int | None = field(
        default_factory=lambda: int(v) if (v := _get_env("KITCHEN_GROUP_ID", "")) else None
    )

    @property
    def WEBHOOK_URL(self) -> str:
        return f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"


# Global config obyekti - butun loyiha shundan foydalanadi
config = Config()
