from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  

from app.settings import settings 


class SessionDB:  
    """Класс для управления асинхронным подключением к базе данных."""
    
    def __init__(self) -> None:  
        self._engine = create_async_engine(
            url=settings.db_settings.get_url_db, 
            echo=settings.db_settings.echo_db
        )  
        
        # фабрика для асинхронной сессии
        self._session_factory = async_sessionmaker(
            bind=self._engine, 
            expire_on_commit=False, 
            autocommit=False
        )  

    @property  
    def get_session(self) -> async_sessionmaker[AsyncSession]:  
        """Метод для получения сессии"""

        return self._session_factory
