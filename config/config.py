import logging
from os.path import abspath, dirname, join

from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from .secret import BOT_TOKEN

app_dir = abspath(dirname(dirname(__file__)))
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(asctime)s: %(message)s\n')


class Config:
    token = BOT_TOKEN
    bot = Bot(token=token, parse_mode='HTML')
    dp = Dispatcher(bot)
    URI_DB = 'sqlite:///' + join(app_dir, 'app.db')
