import logging

from aiogram import types

from database import Session
from database.models import User
from .fun import is_user


def message_log(function):
    async def warped(message: types.Message):
        logging.info(f'Входящее сообщение:\n{message}')
        answer = await function(message)
        if not await is_user(message.from_user.id):
            user = User(message.from_user)
            session = Session()
            session.add(user)
            session.commit()
            logging.info(f'Создан новый пользователь {user}')
        logging.info(f'Исходящее сообщение:\n{answer}')

    return warped
