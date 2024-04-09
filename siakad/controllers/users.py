from typing import Any
from sqlmodel import Session, select

from config.security import get_password_hash
from models.users import User, UserCreate, UserUpdate


def user_create(session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
        
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def user_update(session: Session, user_update: UserUpdate, db_user: User) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    

def get_user_by_email_or_username(*, session: Session, email: str, username: str) -> User | None:
    statement = select(User).where(User.email == email or User.username == username)
    session_user = session.exec(statement).first()
    return session_user
