from aiogram.types import Message


async def start(message: Message):
    return await message.answer(f'Здравтсвуйте, я бот')


async def help(message: Message):
    return await message.answer(f'Список комманд:\n'
                                f'/start - в любой непонятной ситуации\n'
                                f'/help - это сообщение\n'
                                f'/settings - настройки профиля\n'
                                f'/goods - список товаров\n'
                                f'/cart - текущая корзина')


async def settings(message: Message):
    return await message.answer(f'Настройки профиля')


async def goods(message: Message):
    return await message.answer(f'Список товаров')


async def cart(message: Message):
    return await message.answer(f'Текущая корзина')
