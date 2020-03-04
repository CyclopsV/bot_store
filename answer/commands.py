from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup

from .answer import StaticMessage
from .fun import get_order, edit_last_bot_msg
from .keyboards import Keyboard, InlineKeyboard


async def start(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    answer: str = await StaticMessage().start_msg(user_id=message.from_user.id)
    keyboard: ReplyKeyboardMarkup = await Keyboard().help()
    return await message.answer(text=answer, reply_markup=keyboard)


async def help(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    answer: str = await StaticMessage().help(message.from_user.id)
    keyboard: ReplyKeyboardMarkup = await Keyboard().base()
    return await message.answer(text=answer, reply_markup=keyboard)


async def settings(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    answer: str = await StaticMessage().profile(message.from_user.id)
    keyboard: InlineKeyboardMarkup = await InlineKeyboard().profile(message.from_user.id)
    return await message.answer(text=answer, reply_markup=keyboard)


async def goods(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    answer: str = await StaticMessage().goods(message.from_user.id)
    keyboard: InlineKeyboardMarkup = await InlineKeyboard().filter_product(message.from_user.id)
    return await message.answer(text=answer, reply_markup=keyboard)


async def cart(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    return await get_order(message=message)


async def admin(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    answer_msg: str = await StaticMessage().admin(message.from_user.id)
    return await message.answer(text=answer_msg)


async def cancel(message: Message) -> Message:
    return await message.answer(text=await StaticMessage().cancel_msg(message.from_user.id))


async def get_product(message: Message) -> Message:
    await edit_last_bot_msg(message.from_user.id)
    return await message.answer(text=await StaticMessage().get_product_msg(message.from_user.id))
