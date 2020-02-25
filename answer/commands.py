from aiogram.types import Message
import logging


async def start(message: Message):
    logging.info(f'Входящее сообщение:\n{message}')
    await message.answer('Здравтсвуйте, я бот')
