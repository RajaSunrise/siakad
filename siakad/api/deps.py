from collections.abc import Generator
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from pydantic import ValidationError

# moudule bawaaan
from config.db import engine
from config.config import (
    ALGORITHM, SECRET_KEY,
    API_V1_STR
)

from models.users import User
from models.token import TokenPayload

reusable_outh2 = OAuth2PasswordBearer(
    tokenUrl=f"{API_V1_STR}/login/access-token",
)


def get_db()-> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_outh2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        paload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**paload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="could not validate credentials"
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
            )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="inactive users"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The user doesn't have enough privileges"
        )
    return current_user