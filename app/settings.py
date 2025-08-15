from pydantic import SecretStr  
from pydantic_settings import BaseSettings, SettingsConfigDict 
from passlib.context import CryptContext
from typing import ClassVar
import secrets


class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = '.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )


class SettingsDb(ModelConfig):
    """Класс для данных бд"""

    type_and_driver_db: str
    name_db: str
    user_db: str
    password_db: SecretStr
    host_db: str
    port_db: int
    echo_db: bool

    @property  
    def get_url_db(self):  
        """Метод вернёт url для подключения бд"""

        return (f'{self.type_and_driver_db}://{self.user_db}:{self.password_db.get_secret_value()}'
                f'@{self.host_db}:{self.port_db}/{self.name_db}')
    

class Settings(ModelConfig):
    """Класс для данных конфига"""
    
    db_settings: SettingsDb = SettingsDb()
    pwd_context: ClassVar[CryptContext] = CryptContext(schemes=['bcrypt'], deprecated='auto')
    jwt_secret: str = secrets.token_urlsafe(32)
    jwt_alg: str
    access_ttl_seconds: int
    refresh_ttl_seconds: int


settings = Settings()
