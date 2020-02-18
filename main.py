from aiogram.types import Message
from aiogram.utils import executor
from datetime import datetime

from config import Config

dp = Config.dp


@dp.message_handler(commands=['start'])
async def start_command_process(message: Message):
    await message.reply(text=message.text)


@dp.message_handler()
async def other_message(message: Message):
    await message.reply(message.text)


if __name__ == '__main__':
    print(f'Бот запущен {datetime.today()}')
    executor.start_polling(dp)
