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


class TokenPair(BaseModel):
    """Схема для токенов"""
    
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenAccess(BaseModel):
    """Схема для access токена"""

    access_token: str
    token_type: str = 'bearer'


class LogoutUser(BaseModel):
    """Схема для разлогирования пользователя"""
    
    id: str
    email: EmailStr


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


class ActiveUserRequest(BaseModel):
    """Схема данных для смены активности статуса пользователя"""

    is_active: bool


class VerifyUser(BaseModel):
    """Схема данных для верификации пользователя"""

    id: UUID | str
    is_verified: bool = True


class SessionUser(BaseModel):
    """Схема данных для сессии пользователя"""

    user_id: UUID | str
    token: str
    expire_at: datetime
