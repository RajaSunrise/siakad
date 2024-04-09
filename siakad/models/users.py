from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=15, min_length=8)
    email: str = Field(unique=True, index=True, max_length=50)
    photo_path: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserCreateOpen(SQLModel):
    username: str
    email: str
    password: str = Field(default=None)


class UserUpdate(UserBase):
    username: str | None = None
    email: str | None = None
    password: str | None = None


class UserUpdateMe(SQLModel):
    username: str | None = None
    email: str | None = None
    photo_path: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    hash_password: str


class UserOut(UserBase):
    id: int
    photo_path: str | None = None


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


class NewPassword(SQLModel):
    token: str
    new_password: str


class Message(SQLModel):
    message: str
