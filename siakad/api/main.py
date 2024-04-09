from fastapi import APIRouter

from .routes import user, login, register

api_router = APIRouter()

# routes include
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(register.router, prefix="/register", tags=["register"])
