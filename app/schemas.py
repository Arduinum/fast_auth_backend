from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterUser(BaseModel):
    """Схема регистрации пользователя"""

    email: EmailStr
    passwd: str = Field(..., min_length=8)
    name: str
    surname: str
    patronymic: str


class LoginUser(BaseModel):
    """Схема для логина пользователя"""

    email: EmailStr
    passwd: str = Field(..., min_length=8)


class GetUserData(BaseModel):
    """Схема данных пользователя"""

    class Config:
        frozen = True

    id: UUID | str
    name: str
    surname: str
    patronymic: str
    email: EmailStr


class GetAllUserData(GetUserData):
    """Схема для получения всех данных пользователя"""

    hash_passwd: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime


class EditUser(BaseModel):
    """Схема для редактирования пользователя"""

    name: str
    surname: str
    patronymic: str
    email: EmailStr
    hash_passwd: str = Field(..., min_length=8)


class EditUserAdmin(EditUser):
    """Схема для редактирования пользователя администратором"""

    is_active: bool
    is_verified: bool
    is_admin: bool


class ChangePasswd(BaseModel):
    """Схема данных для смены пароля пользователя"""

    old_passwd: str = Field(..., min_length=8)
    new_passwd: str = Field(..., min_length=8)
