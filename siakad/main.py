from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import SQLModel
from starlette_admin.contrib.sqlmodel import Admin, ModelView

from config import config
from api.main import api_router
from config.db import engine
from models.users import User


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url=f"{config.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


app.include_router(api_router, prefix=config.API_V1_STR)


# admin routes
def init_database() -> None:
    SQLModel.metadata.create_all(engine)

# Create admin
admin = Admin(engine, title="Example: SQLModel")

# admin view 
admin.add_view(ModelView(User, icon="fa fa-users"))

# admin app
admin.mount_to(app)
