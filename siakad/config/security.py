from datetime import datetime, timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext

from .config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_acces_token(subject: str | Any, expires_time: timedelta) -> str:
    expire = datetime.utcnow() + expires_time
    to_encode = {"exp": expire, "sub": str(subject)}
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)