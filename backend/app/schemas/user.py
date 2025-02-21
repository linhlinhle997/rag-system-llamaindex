from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDetail(UserBase):
    id: int
