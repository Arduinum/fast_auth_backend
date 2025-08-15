from fastapi import HTTPException, status
from sqlalchemy import select, insert, delete, update
from uuid import UUID
from typing import Literal

from app.database.models import User, UserSessions
from app.database.session import SessionDB
from app.schemas import (
    ChangePasswd, 
    RegisterUser, 
    GetAllUserData, 
    GetUserData, 
    EditUser, 
    EditUserAdmin,
    LoginUser,
    VerifyUser,
    SessionUser
)
from app.settings import settings


async def get_user_list() -> list[GetUserData]:
    """Получает список всех пользователей"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = select(
            User.id,
            User.name,
            User.surname,
            User.patronymic,
            User.email
        ).order_by(User.created_at.asc())

        result = await async_session.execute(query)
        users = result.mappings().fetchall()

        return [
            GetUserData.model_validate(
                obj=accept, 
                from_attributes=True
            ) for accept in users
        ]

async def get_user_admin(user_id: UUID) -> GetAllUserData | None:
    """Получает все данные пользователя (для администратора)"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = select(
            User.id,
            User.name,
            User.surname,
            User.patronymic,
            User.email,
            User.created_at,
            User.hash_passwd,
            User.is_active,
            User.is_admin,
            User.is_verified
        ).where(user_id == User.id)
        
        result = await async_session.execute(query)
        user = result.mappings().first()

        return GetAllUserData.model_validate(obj=user, from_attributes=True)


async def get_user(user_id: UUID) -> GetUserData | None:
    """Получает данные пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = select(
            User.id,
            User.name,
            User.surname,
            User.patronymic,
            User.email
        ).where(user_id == User.id)
        
        result = await async_session.execute(query)
        user = result.mappings().first()

        return GetUserData.model_validate(obj=user, from_attributes=True)


async def del_user(user_id: UUID) -> None:
    """Удаляет пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = delete(User).where(user_id == User.id)
        
        await async_session.execute(query)
        await async_session.commit()


async def make_active_user(user_id: UUID, is_active: bool) -> None:
    """Делает пользователя активным/неактивным"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = update(User).where(user_id == User.id).values(is_active=is_active).execution_options(
            synchronize_session='fetch')

        await async_session.execute(query)
        await async_session.commit()


async def new_user(valid_model: EditUserAdmin | RegisterUser) -> None:
    """Создаёт пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        hash_passwd = settings.pwd_context.hash(valid_model.passwd)
        
        query = insert(User).values(
            name=valid_model.name,
            surname=valid_model.surname,
            patronymic=valid_model.patronymic,
            email=valid_model.email,
            hash_passwd=hash_passwd
        )
        
        await async_session.execute(query)
        await async_session.commit()


async def edit_user(user_id: UUID, valid_model: EditUser | EditUserAdmin) -> None:
    """Редактирует пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = update(User).where(user_id == User.id).values(**valid_model.model_dump())

        await async_session.execute(query)
        await async_session.commit()


async def change_password(user_id: UUID, valid_model: ChangePasswd) -> None:
    """Меняет пароль пользователя"""
    
    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        result = await async_session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')

        if not settings.pwd_context.verify(valid_model.old_passwd, user.hash_passwd):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Старый пароль неверный!')

        new_hashed = settings.pwd_context.hash(valid_model.new_passwd)

        query = update(User).where(User.id == user_id).values(hash_passwd=new_hashed)
        await async_session.execute(query)
        await async_session.commit()


async def user_in_system(valid_model: LoginUser) -> str:
    """Проверяет есть ли пользователь в системе"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        result = await async_session.execute(select(User).where(User.email == valid_model.email))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')
        
        if not settings.pwd_context.verify(valid_model.passwd, user.hash_passwd):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пароль неверный!')
        
        return str(user.id)


async def user_in_system_by_id(user_id: str) -> str:
    """Проверяет есть ли пользователь в системе по id"""

    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный формат user_id!')    

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        result = await async_session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')
        
        return str(user.id)


async def verified_user(valid_model: VerifyUser) -> None:
    """Верифицирует пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = update(User).where(User.id == valid_model.id).values(
            is_verified=valid_model.is_verified).execution_options(synchronize_session='fetch')

        result = await async_session.execute(query)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')

        await async_session.commit()


async def create_user_session(valid_model: SessionUser) -> None:
    """Создаёт сессию пользователя"""
    
    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = insert(UserSessions).values(**valid_model.model_dump())

        await async_session.execute(query)
        await async_session.commit()


async def deactivate_user_session(user_id: str) -> None:
    """Деактивирует сессию пользователя"""
    
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный формат user_id!')    

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = update(UserSessions).where(UserSessions.user_id == user_id, UserSessions.is_active.is_(True)).values(
            is_active=False).execution_options(synchronize_session='fetch')

        result = await async_session.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сессия не найдена!')

        await async_session.commit()


async def check_user_session(token: str) -> bool:
    """Проверяет активна ли текущая сессия по refresh токену"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = select(UserSessions).where(UserSessions.token == token, UserSessions.is_active.is_(True))

        result = await async_session.execute(query)
        result = result.scalar_one_or_none( )

        return result is not None


async def get_user_role(user_id: UUID | str) -> Literal['admin', 'user', 'guest']:
    """Возвращает роль пользователя по его ID"""
    
    if isinstance(user_id, str):
        try:
            user_id = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный формат user_id!') 

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            if user.is_admin:
                return 'admin'
            else:
                return 'user'

        return 'guest'
