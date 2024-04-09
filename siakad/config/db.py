from sqlmodel import Session, create_engine, SQLModel, select
from models.users import User, UserCreate
from .config import FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD
from controllers.users import user_create

engine = create_engine("mysql+pymysql://root:indra@localhost/siakad")

SQLModel.metadata.create_all(engine)

def init_db(session: Session) -> None:
    user = session.exec(
        select(User).where(User.email == FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=FIRST_SUPERUSER,
            password=FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_create(session=session, user_create=user_in)


