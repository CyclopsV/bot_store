from aiogram.types import Message
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError
import logging


from config import Config
from answer import commands

dp = Config.dp


@dp.message_handler(commands=['start'])
async def start_command_process(message: Message):
    await commands.start(message)


@dp.message_handler()
async def other_message(message: Message):
    await message.reply(message.text)


if __name__ == '__main__':
    logging.info('Старт приложения')
    try:
        executor.start_polling(dp)
    except NetworkError:
        logging.exception('Не удалось подключиться к серверу телеграмма. (Проверьте подключение к сети, vpn, proxy)')
