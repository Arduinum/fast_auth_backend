from app.database.user_cruds import new_user
from app.schemas import EditUserAdmin
from asyncio import run


async def seed_fake_users() -> None:
    """Создаёт фейковых пользователей бд"""

    # администратор
    await new_user(valid_model=EditUserAdmin(
        name='Вася',
        surname='Огурцов',
        patronymic='Михайлович',
        email='test1@yandex.ru',
        hash_passwd='ddwadwdwreffrgrgrgrrgrgrg#',
        is_active=True,
        is_verified=True,
        is_admin=True
    ))

    # обычный пользователь
    await new_user(valid_model=EditUserAdmin(
        name='Саша',
        surname='Цветков',
        patronymic='Михайлович',
        email='test2@yandex.ru',
        hash_passwd='ddwaffedwdwreffrgrgrgrrgrgrg#',
        is_active=True,
        is_verified=True,
        is_admin=False
    ))

    # удалённый пользователь
    await new_user(valid_model=EditUserAdmin(
        name='Евгений',
        surname='Стрельцов',
        patronymic='Михайлович',
        email='test3@yandex.ru',
        hash_passwd='dffedwdwreffrgrgrgrrgrgrg#',
        is_active=False,
        is_verified=True,
        is_admin=False
    ))

    # не верефецированный пользователь
    await new_user(valid_model=EditUserAdmin(
        name='Ваня',
        surname='Иванов',
        patronymic='Михайлович',
        email='test4@yandex.ru',
        hash_passwd='dffedwgrgrrgrgrg#',
        is_active=True,
        is_verified=False,
        is_admin=False
    ))


def start_seed_users() -> None:
    """Запускает процесс заполнения данных пользователя"""

    try:
        run(seed_fake_users())
    except KeyboardInterrupt:
        pass
