import logging
from datetime import datetime

from aiogram import types

from database import Session
from database.models import User
from .fun import is_user


def message_log(function):
    async def warped(message: types.Message):
        logging.info(f'Входящее сообщение:\n{message}')
        answer = await function(message)
        session = Session()
        if await is_user(message.from_user.id):
            user = session.query(User).filter(User.id == message.from_user.id).first()
            user.date_last_use = datetime.today()
            if user.user_name != message.from_user.username:
                user.user_name = message.from_user.username
                logging.info(f'Обновлено имя пользователя {user}')
        else:
            user = User(message.from_user)
            session.add(user)
            logging.info(f'Создан новый пользователь {user}')
        session.commit()
        logging.info(f'Исходящее сообщение:\n{answer}')

    return warped


def callback_log(function):
    async def warped(callback_query: types.CallbackQuery):
        logging.info(f'Нажата кнопка:\n{callback_query}')
        answer = await function(callback_query)
        session = Session()
        user = session.query(User).filter(User.id == callback_query.from_user.id).first()
        user.date_last_use = datetime.today()
        if user.user_name != callback_query.from_user.username:
            user.user_name = callback_query.from_user.username
            logging.info(f'Обновлено имя пользователя {user}')
        session.commit()
        logging.info(f'Отправлен ответ:\n{answer}')
    return warped
