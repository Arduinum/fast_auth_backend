from fastapi import FastAPI

import uvicorn
from app.routes.routes_user import auth_router
from app.middleware.auth import AuthMiddleware


app = FastAPI()
# подключение роутов
app.include_router(router=auth_router)
# подключение middleware
app.add_middleware(AuthMiddleware, required_role='admin')


def start_app():
    """Запускает приложение"""

    uvicorn.run(app='app.main:app', reload=True)
