from fastapi import APIRouter, Depends, Request, status, Path, Body
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.schemas import (
    GetUserData, 
    GetAllUserData, 
    ActiveUserRequest,
    EditUserAdmin,
    RegisterUser,
    EditUser,
    ChangePasswd,
    LoginUser,
    TokenPair,
    TokenAccess,
    VerifyUser,
    SessionUser
)
from app.database.user_cruds import (
    get_user_list, 
    get_user_admin, 
    get_user, 
    del_user,
    make_active_user,
    new_user,
    edit_user,
    change_password,
    user_in_system,
    user_in_system_by_id,
    verified_user,
    create_user_session,
    deactivate_user_session,
    get_user_role
)

from app.utils.jwt_utils import create_token, get_headers_token
from app.settings import settings
from app.dependencies.auth import validate_refresh_token
from app.dependencies.role import require_admin, require_user


auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.get('/admin/users', response_model=list[GetUserData], status_code=status.HTTP_200_OK)
async def list_users(data: dict = Depends(require_admin)) -> list[GetUserData]:
    """Получает список пользователей"""

    users = await get_user_list()
    return users


@auth_router.get('/admin/users/{user_id}', response_model=GetAllUserData, status_code=status.HTTP_200_OK)
async def get_user_for_admin(
    user_id: UUID = Path(..., description='ID пользователя'),
    data: dict = Depends(require_admin)) -> GetAllUserData:
    """Получает все данные пользователя (для администратора)"""

    user = await get_user_admin(user_id=user_id)
    return user


@auth_router.get('/users/{user_id}', response_model=GetUserData, status_code=status.HTTP_200_OK)
async def get_user_for_user(
    user_id: UUID = Path(..., description='ID пользователя'),
    data: dict = Depends(require_user)) -> GetUserData:
    """Получает данные пользователя (для простого пользователя)"""

    user = await get_user(user_id=user_id)
    return user


@auth_router.patch('/admin/users/{user_id}/status', status_code=status.HTTP_204_NO_CONTENT)
async def status_user(
    user_id: UUID = Path(..., description='ID пользователя'),
    body: ActiveUserRequest = Body(...),
    data: dict = Depends(require_admin)) -> None:
    """Меняет статус активности пользователя"""

    await make_active_user(user_id=user_id, is_active=body.is_active)


@auth_router.delete('/admin/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID = Path(..., description='ID пользователя'),
    data: dict = Depends(require_admin)) -> None:
    """Полностью удаляет пользователя"""

    await del_user(user_id=user_id)


@auth_router.post('/admin/users', status_code=status.HTTP_201_CREATED)
async def create_user_for_admin(
    body: EditUserAdmin = Body(...),
    data: dict = Depends(require_admin)) -> None:
    """Создаёт нового пользователя со всеми полями (для администратора)"""

    await new_user(valid_model=body)


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user_register(body: RegisterUser = Body(...)) -> None:
    """Создаёт нового пользователя при регистрации"""

    await new_user(valid_model=body)


@auth_router.patch('/admin/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user_for_admin(
    user_id: UUID = Path(..., description='ID пользователя'), 
    body: EditUserAdmin = Body(...),
    data: dict = Depends(require_admin)) -> None:
    """Редактирует все поля пользователя (для администратора)"""

    await edit_user(user_id=user_id, valid_model=body)


@auth_router.patch('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user_for_user(
    user_id: UUID = Path(..., description='ID пользователя'), 
    body: EditUser = Body(...),
    data: dict = Depends(require_user)) -> None:
    """Редактирует все поля пользователя (для пользователя)"""

    await edit_user(user_id=user_id, valid_model=body)


@auth_router.patch('/users/{user_id}/password', status_code=status.HTTP_204_NO_CONTENT)
async def update_passwd(
    request: Request,
    user_id: UUID = Path(..., description='ID пользователя'),
    body: ChangePasswd = Body(...),
    data: dict = Depends(require_user)) -> None:
    """Обновляет пароль пользователя"""

    token = get_headers_token(request=request)
    await change_password(user_id=user_id, valid_model=body)
    await deactivate_user_session(token=token)
    user_role = await get_user_role(user_id=user_id)

    refresh_token = create_token(
        sub=user_id, 
        ttl_seconds=settings.refresh_ttl_seconds, 
        token_type='refresh',
        user_rоle=user_role
    )
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=settings.refresh_ttl_seconds)
    await create_user_session(valid_model=SessionUser(
        user_id=user_id,
        token=refresh_token,
        expire_at=expire_at
    ))

    token_pair = TokenPair(
        access_token=create_token(
            sub=user_id, 
            ttl_seconds=settings.access_ttl_seconds, 
            token_type='access',
            user_rоle=user_role
        ),
        refresh_token=refresh_token
    )
    
    return token_pair


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(body: LoginUser = Body(...)) -> TokenPair:
    """Логинит пользователя в систему"""

    # получаем id пользователя если он есть в системе
    user_in_sys = await user_in_system(valid_model=body)

    # если пользователь есть в системе, то создаём новую пару токенов
    if user_in_sys:
        user_role = await get_user_role(user_id=user_in_sys)

        refresh_token = create_token(
            sub=user_in_sys, 
            ttl_seconds=settings.refresh_ttl_seconds, 
            token_type='refresh',
            user_rоle=user_role
        )
        expire_at = datetime.now(timezone.utc) + timedelta(seconds=settings.refresh_ttl_seconds)
        await create_user_session(valid_model=SessionUser(
            user_id=user_in_sys,
            token=refresh_token,
            expire_at=expire_at
        ))
        
        token_pair = TokenPair(
            access_token=create_token(
                sub=user_in_sys, 
                ttl_seconds=settings.access_ttl_seconds, 
                token_type='access',
                user_rоle=user_role
            ),
            refresh_token=refresh_token
        )
        
        return token_pair


@auth_router.post('/refresh', status_code=status.HTTP_200_OK)
async def refresh_access_token(
    data: dict = Depends(validate_refresh_token), 
    user: dict = Depends(require_user)) -> TokenAccess:
    """Обновляет access токен"""

    user_role = await get_user_role(user_id=data.get('user'))

    # генерация нового access токена
    new_access_token = TokenAccess(
        access_token=create_token(
            sub=data.get('user'), 
            ttl_seconds=settings.access_ttl_seconds, 
            token_type='access',
            user_rоle=user_role
        )
    )

    return new_access_token


@auth_router.post('/logout', status_code=status.HTTP_200_OK)
async def logout_user(user: dict = Depends(require_user)) -> None:
    """Разлогинивает пользователя из системы"""

    await deactivate_user_session(user_id=user.get('sub'))


@auth_router.post('/verify', status_code=status.HTTP_204_NO_CONTENT)
async def virify_user(body: VerifyUser = Body(...), data: dict = Depends(require_admin)) -> None:
    """Верифицирует пользователя"""

    user_in_sys = await user_in_system_by_id(user_id=body.id)

    if user_in_sys:
        await verified_user(valid_model=body)
