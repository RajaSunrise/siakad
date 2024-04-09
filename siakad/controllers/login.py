from sqlmodel import Session
from config.security import verify_password
from controllers.users import get_user_by_email_or_username
from models.users import User

def authentication(session: Session, email_or_username: str, password: str) -> User:
    # Cari user berdasarkan email atau username
    db_user = get_user_by_email_or_username(session=session, email=email_or_username, username=email_or_username)
    if not db_user:
        return None
    # Verifikasi password
    if not verify_password(password, db_user.hash_password):
        return None
    return db_user
