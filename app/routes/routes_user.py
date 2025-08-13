from fastapi import APIRouter, status, Path, Response, Body
from uuid import UUID

from app.schemas import (
    GetUserData, 
    GetAllUserData, 
    ActiveUserRequest,
    EditUserAdmin,
    RegisterUser,
    EditUser,
    ChangePasswd
)
from app.database.user_cruds import (
    get_user_list, 
    get_user_admin, 
    get_user, 
    del_user,
    make_active_user,
    new_user,
    edit_user,
    change_password
)


auth_router = APIRouter(prefix='/auth', tags=['auth'])


# проверен
@auth_router.get('/users', response_model=list[GetUserData], status_code=status.HTTP_200_OK)
async def list_users() -> list[GetUserData]:
    """Получает список пользователей"""

    users = await get_user_list()
    return users


# проверен
@auth_router.get('/admin/users/{user_id}', response_model=GetAllUserData, status_code=status.HTTP_200_OK)
async def get_user_for_admin(user_id: UUID = Path(..., description='ID пользователя')) -> GetAllUserData:
    """Получает все данные пользователя (для администратора)"""

    user = await get_user_admin(user_id=user_id)
    return user


# проверен
@auth_router.get('/users/{user_id}', response_model=GetUserData, status_code=status.HTTP_200_OK)
async def get_user_for_user(user_id: UUID = Path(..., description='ID пользователя')) -> GetUserData:
    """Получает данные пользователя (для простого пользователя)"""

    user = await get_user(user_id=user_id)
    return user

# проверен
@auth_router.patch('/admin/users/{user_id}/status', status_code=status.HTTP_204_NO_CONTENT)
async def status_user(
    user_id: UUID = Path(..., description='ID пользователя'),
    body: ActiveUserRequest = Body(...)) -> None:
    """Меняет статус активности пользователя"""

    await make_active_user(user_id=user_id, is_active=body.is_active)


# проверен
@auth_router.delete('/admin/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID = Path(..., description='ID пользователя')) -> None:
    """Полностью удаляет пользователя"""

    await del_user(user_id=user_id)

# проверен
@auth_router.post('/admin/users', status_code=status.HTTP_201_CREATED)
async def create_user_for_admin(body: EditUserAdmin = Body(...)) -> None:
    """Создаёт нового пользователя со всеми полями (для администратора)"""

    await new_user(valid_model=body)


# проверен
@auth_router.post('/users', status_code=status.HTTP_201_CREATED)
async def create_user_register(body: RegisterUser = Body(...)) -> None:
    """Создаёт нового пользователя при регистрации"""

    await new_user(valid_model=body)


# проверен
@auth_router.patch('/admin/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user_for_admin(
    user_id: UUID = Path(..., description='ID пользователя'), 
    body: EditUserAdmin = Body(...)) -> None:
    """Редактирует все поля пользователя (для администратора)"""

    await edit_user(user_id=user_id, valid_model=body)

# проверен
@auth_router.patch('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user_for_user(
    user_id: UUID = Path(..., description='ID пользователя'), 
    body: EditUser = Body(...)) -> None:
    """Редактирует все поля пользователя (для пользователя)"""

    await edit_user(user_id=user_id, valid_model=body)


@auth_router.patch('/users/{user_id}/password')
async def update_passwd(
    user_id: UUID = Path(..., description='ID пользователя'),
    body: ChangePasswd = Body(...)) -> None:
    """Обновляет пароль пользователя"""

    await change_password(user_id=user_id, valid_model=body)
