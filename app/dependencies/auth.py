from fastapi import HTTPException, status, Request

from app.utils.jwt_utils import get_headers_token, decode_token
from app.database.user_cruds import user_in_system_by_id


async def validate_refresh_token(request: Request) -> dict:
    """Зависимость для проверки refresh токена"""
    
    token = get_headers_token(request)
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Недействительный токен!')
    
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Токен не refresh типа!')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='В токене нет id пользователя!')

    user_in_sys = await user_in_system_by_id(user_id=user_id)
    if not user_in_sys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден!')

    return {'user': user_in_sys, 'payload': payload}
