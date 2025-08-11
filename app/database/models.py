import uuid 
from sqlalchemy import UUID  
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Text, DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """Базовая модель для корректной работы аннотаций"""

    pass


class User(Base):  
    """Модель пользователя"""
    
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4,
        name='id'
    )

    name: Mapped[str] = mapped_column(
        String(120),
        name='имя',
        nullable=False
    )

    surname: Mapped[str] = mapped_column(
        String(120),
        name='фамилия',
        nullable=False
    )

    patronymic: Mapped[str] = mapped_column(
        String(120),
        name='отчество',
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100), 
        name='эл_почта',
        unique=True, 
        nullable=False
    )

    hash_passwd: Mapped[str] = mapped_column(
        Text,
        name='пароль', 
        unique=False, 
        nullable=False
    )  

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        name='активный',
        default=False, 
        nullable=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        name='подтверждён',
        default=False, 
        nullable=False
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean, 
        name='админ',
        default=False, 
        nullable=False
    ) 

    created_at: Mapped[datetime] = mapped_column(  
        DateTime(timezone=True), 
        server_default=func.now(), 
        default=datetime.now  
    )
