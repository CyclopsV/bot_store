import logging

from aiogram.types import Message
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError

from answer import commands, handlers
from config import Config

dp = Config.dp


@dp.message_handler(commands=['start'])
@handlers.message_log
async def start_command_process(message: Message):
    return await commands.start(message)


@dp.message_handler(commands=['help'])
@handlers.message_log
async def help_command_process(message: Message):
    return await commands.help(message)


@dp.message_handler(commands=['settings'])
@handlers.message_log
async def settings_command_process(message: Message):
    return await commands.settings(message)


@dp.message_handler(commands=['goods'])
@handlers.message_log
async def goods_command_process(message: Message):
    return await commands.goods(message)


@dp.message_handler(commands=['cart'])
@handlers.message_log
async def cart_command_process(message: Message):
    return await commands.cart(message)


@dp.message_handler()
@handlers.message_log
async def other_message(message: Message):
    print(type(message.from_user.id))
    return await message.reply(message.text)


if __name__ == '__main__':
    logging.info('Старт приложения')
    try:
        executor.start_polling(dp)
    except NetworkError:
        logging.exception('Не удалось подключиться к серверу телеграмма. (Проверьте подключение к сети, vpn, proxy)')
