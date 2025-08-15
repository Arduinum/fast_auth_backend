from fastapi import HTTPException, Request, status
import jwt
from datetime import datetime, timedelta, timezone
from app.settings import settings


def create_token(sub: str, ttl_seconds: int, token_type: str, user_rоle: str) -> str:
    """Создаёт токен"""
    
    now = datetime.now(timezone.utc)
    payload = {
        'sub': sub,
        'type': token_type,
        'role': user_rоle,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> dict:
    """Декодирует токен"""
    
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except jwt.ExpiredSignatureError:
        raise ValueError('Срок действия токена истек!')
    except jwt.InvalidTokenError:
        raise ValueError('Недействительный токен!')


def get_headers_token(request: Request) -> str:
    """Получение токена refrash из headers"""

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Отсутствует токен!')

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Некорректный формат токена!')

    return token