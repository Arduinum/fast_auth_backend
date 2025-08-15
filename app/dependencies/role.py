from typing import Any
from fastapi import Request, HTTPException, status


def require_admin(request: Request) -> Any:
    """Зависимость доступа для роли администратора"""
    
    user = request.state.user
    
    if user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав!'
        )
    
    return user


def require_user(request: Request) -> Any:
    """Зависимость доступа для роли пользователь"""
    
    user = request.state.user
    
    if user.get('role') not in ('admin', 'user'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав!'
        )
    
    return user
