import logging

from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError

from answer import commands, handlers
from answer.answer import answer_text, callback
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


@dp.message_handler(commands=['admin'])
@handlers.message_log
async def admin_command_process(message: Message):
    return await commands.admin(message)


@dp.message_handler(commands=['cancel'])
@handlers.message_log
async def cancel_command_process(message: Message):
    return await commands.cancel(message)


@dp.message_handler(commands=['get_product'])
@handlers.message_log
async def cancel_command_process(message: Message):
    return await commands.get_product(message)


@dp.message_handler(content_types=ContentType.PHOTO)
@handlers.message_log
async def process_photo(message: Message):
    return await answer_text(message)


@dp.callback_query_handler()
@handlers.callback_log
async def process_callback(callback_query: CallbackQuery):
    return await callback(callback_query)


@dp.message_handler()
@handlers.message_log
async def other_message(message: Message):
    return await answer_text(message)


if __name__ == '__main__':
    logging.info('Запуск приложения')
    try:
        executor.start_polling(dp)
    except NetworkError:
        logging.exception('Не удалось подключиться к серверу телеграмма. (Проверьте подключение к сети, vpn, proxy)')
