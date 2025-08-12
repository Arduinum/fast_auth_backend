from fastapi import HTTPException, status
from sqlalchemy import select, insert, delete, update
from uuid import UUID

from app.database.models import User
from app.database.session import SessionDB
from app.schemas import ChangePasswd, RegisterUser, GetAllUserData, GetUserData, EditUser, EditUserAdmin
from app.settings import settings


async def get_user_list() -> list[GetUserData]:
    """Получает список всех пользователей"""

    async with SessionDB.get_session as async_session:
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

    async with SessionDB.get_session as async_session:
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
        ).where(user_id == user.id)
        
        result = await async_session.execute(query)
        user = result.mappings().first()

        return GetAllUserData.model_validate(obj=user, from_attributes=True)


async def get_user(user_id: UUID) -> GetUserData | None:
    """Получает данные пользователя"""

    async with SessionDB.get_session as async_session:
        query = select(
            User.id,
            User.name,
            User.surname,
            User.patronymic,
            User.email
        ).where(user_id == user.id)
        
        result = await async_session.execute(query)
        user = result.mappings().first()

        return GetUserData.model_validate(obj=user, from_attributes=True)


async def del_user(user_id: UUID) -> None:
    """Удаляет пользователя"""

    async with SessionDB.get_session as async_session:
        query = delete(User).where(user_id == User.id)
        await async_session.execute(query)


async def make_active_user(user_id: UUID, is_active: bool) -> None:
    """Делает пользователя активным/неактивным"""

    async with SessionDB.get_session as async_session:
        query = update(User).where(user_id == User.id).values(is_active=is_active).execution_options(
            synchronize_session='fetch')

        await async_session.execute(query)
        await async_session.commit()


async def new_user(valid_model: EditUserAdmin | RegisterUser) -> None:
    """Создаёт пользователя"""

    async_session_factory = SessionDB().get_session
    async with async_session_factory() as async_session:
        query = insert(User).values(**valid_model.model_dump())
        
        await async_session.execute(query)
        await async_session.commit()


async def edit_user(user_id: UUID, valid_model: EditUser | EditUserAdmin) -> None:
    """Редактирует пользователя"""

    async with SessionDB.get_session as async_session:
        query = update(User).where(user_id == User.id).values(**valid_model.model_dump())

        await async_session.execute(query)
        await async_session.commit()


async def change_password(user_id: UUID, data: ChangePasswd) -> None:
    """Меняет пароль пользователя"""
    
    async with SessionDB.get_session as async_session:
        result = await async_session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден!')

        if not settings.pwd_context.verify(data.old_passwd, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Старый пароль неверный!')

        new_hashed = settings.pwd_context.hash(data.new_passwd)

        query = update(User).where(User.id == user_id).values(hashed_password=new_hashed)
        await async_session.execute(query)
        await async_session.commit()
