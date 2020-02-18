import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from .secret import BOT_TOKEN

app_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    token = BOT_TOKEN
    bot = Bot(token=token, parse_mode='HTML')
    dp = Dispatcher(bot)
