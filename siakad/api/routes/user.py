from typing import Any
from fastapi import (
    APIRouter, Depends,
    HTTPException, status,
    UploadFile, File
    )
from sqlmodel import col, delete, func, select

# module bawaan
from api.deps import SessionDep, get_current_active_superuser, CurrentUser, get_current_user
from controllers.users import (
    get_user_by_email_or_username, user_create,
    user_update,
)
from config.security import get_password_hash, verify_password
from models.users import (
    User, UserCreate,
    UserCreateOpen, UserOut,
    UsersOut, UserUpdate,
    UserUpdateMe, UpdatePassword,
    Message
)
from config.config import USERS_OPEN_REGISTRATION
from utils.foto import save_avatar


router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UsersOut)
def read_user(session: SessionDep, skip: int = 0, limit: int = 100)-> Any:
    count_statment = select(func.count()).select_from(User)
    count = session.exec(count_statment).one()

    statment = select(User).offset(skip).limit(limit)
    users = session.exec(statment).all()
    return UsersOut(data=users, count=count)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UsersOut)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    user = get_user_by_email_or_username(session=session, email=user_in.email, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email or username already exists in the system."
        )
    user = user_create(session=session, user_create=user_in)
    return user


@router.patch("/me", response_model=UserOut)
async def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: User = Depends(get_current_user),
    avatar: UploadFile = File(None),
) -> Any:
    if user_in.email or user_in.username:
        existing_user = get_user_by_email_or_username(
            session=session, email=user_in.email, username=user_in.username
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )

    # Update user data
    user_data = user_in.dict(exclude_unset=True)
    if user_in.password:
        user_data["hash_password"] = get_password_hash(user_in.password)

    # Handle avatar upload
    if avatar:
        # Validate file format (assuming it's in utils.py)
        if not avatar.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="File must be an image."
            )

        # Save avatar and update photo_path
        filename = await save_avatar(avatar)
        user_data["photo_path"] = filename

    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user
    

@router.patch("/me/password", response_model=Message)
def update_password_me(*, session: SessionDep, body: UpdatePassword, current_user: CurrentUser) -> Any:
    if not verify_password(body.current_password, current_user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one"
        )
    
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one"
        )
    
    hashed_password = get_password_hash(body.new_password)
    current_user.hash_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserOut)
def read_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=UserOut)
def create_user_open(session: SessionDep, user_in: UserCreateOpen) -> Any:
    if not USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server",
        )
    user = get_user_by_email_or_username(session=session, email=user_in.email, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.from_orm(user_in)
    user = user_create(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserOut)
def read_user_by_id(user_id: int, session: SessionDep, current_user: CurrentUser) -> Any:
    
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserOut,)
def update_user(*, session: SessionDep, user_id: int, user_in: UserUpdate) -> Any:

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = get_user_by_email_or_username(session=session, email=user_in.email, username=user_in.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

    db_user = user_update(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}")
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: int) -> Message:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif user != current_user and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    elif user == current_user and current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves"
        )
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
