from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.utils.jwt_utils import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """Проверяет права и токен"""
    
    def __init__(self, app: FastAPI, required_role: str = None):
        super().__init__(app)
        self.required_role = required_role

    async def dispatch(self, request: Request, call_next: Callable):
        # Пропуск данных путей
        if request.url.path in ['/auth/login', '/auth/register', '/docs', '/redoc', '/openapi.json', '/favicon.ico']:
            return await call_next(request)

        # проверка токена
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'detail': 'Отсутствует токен!'})
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                raise ValueError()
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                content={'detail': 'Некорректный формат токена!'}
            )

        try:
            payload = decode_token(token)
        except ValueError as err:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': str(err)}
            )
        
        if not payload:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'detail': 'Недействительный токен!'})

        request.state.user = payload

        response = await call_next(request)
        return response
