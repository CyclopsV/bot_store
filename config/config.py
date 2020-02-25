from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import logging
import os

from .secret import BOT_TOKEN

app_dir = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(asctime)s: %(message)s\n')


class Config:
    token = BOT_TOKEN
    bot = Bot(token=token, parse_mode='HTML')
    dp = Dispatcher(bot)
    URI_DB = 'sqlite:///' + os.path.join(app_dir, 'app.db')
