from fastapi import FastAPI

import uvicorn
from app.routes.routes_user import auth_router


app = FastAPI()
app.include_router(router=auth_router)


def start_app():
    """Запускает приложение"""

    uvicorn.run(app='app.main:app', reload=True)
