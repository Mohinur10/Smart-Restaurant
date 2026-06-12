"""Parollarni xavfsiz hash qilish (PBKDF2 + SECRET_KEY)."""
import hashlib
import hmac

from app.config import config


def hash_password(raw_password: str) -> str:
    """Parolni SECRET_KEY tuz (salt) sifatida ishlatib hash qiladi."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        config.SECRET_KEY.encode("utf-8"),
        100_000,
    ).hex()


def verify_password(raw_password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(raw_password), hashed)
