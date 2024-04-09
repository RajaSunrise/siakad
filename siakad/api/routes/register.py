from typing import Any
from fastapi import APIRouter, HTTPException

from api.deps import SessionDep
from controllers.users import get_user_by_email_or_username
from controllers.register import register_user
from models.users import UserCreate, UsersOut


router = APIRouter()

@router.post("/", response_model=UsersOut)
def register(*, session: SessionDep, user_in: UserCreate) -> Any:
    user = get_user_by_email_or_username(session=session, email=user_in.email, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email or username already exists in the system."
        )
    user = register_user(session=session, user_create=user_in)
    return user
