from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone, func
from jose import jwt

from backend.app.core.config import settings


def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

    hashed = pwd_context.hash(password)
    return hashed


def verify_password(plain: str, hashed: str) -> bool:
    pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

    is_valid = pwd_context.verify(plain, hashed)
    return is_valid


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire_in = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire_in
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token
