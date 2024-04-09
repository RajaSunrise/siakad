from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm


from models.users import UserOut
from api.deps import SessionDep
from controllers.login import authentication
from config.security import create_acces_token
from config import config


router = APIRouter()


@router.post("/", response_model=UserOut)
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = authentication(session=session, email_or_username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or username and password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)  # Atur waktu kedaluwarsa token
    access_token = create_acces_token(subject=user.id, expires_time=access_token_expires)  # Sertakan expires_time
    return {"access_token": access_token, "token_type": "bearer"}

