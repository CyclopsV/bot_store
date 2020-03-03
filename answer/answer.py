from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from .fun import is_user, get_profile, edit_last_bot_msg, is_last_bot_message, other_answer, is_admin, \
    callback_edit_profile, callback_order, callback_product, callback_filter, InlineKeyboard, callback_edit_product, \
    add_product
from .statiс import edit_admin, get_product, edit, order, prod


class Store:
    name = 'Название магазина'
    url = 'Ссылка на магазин'


class StaticMessage:

    async def start_msg(self, user_id: int) -> str:
        if await is_user(user_id):
            answer: str = f'Здравствуйте, этот бот предназначен, для оформления заказов в <a href="{Store.url}">' \
                          f'{Store.name}</a>\n\nПожалуйста просмотрите справку по боту /help'
        else:
            answer: str = f'И снова здравствуйте, напоминаем, что это бот принимает заказы в <a href="{Store.url}">' \
                          f'{Store.name}</a>\n\nЧто бы вспомнить комманды, воспользуйтесь коммандой /help'
        return answer

    async def help(self, user_id: int) -> str:
        help_msg: str = f'Список комманд:\n/start - в любой непонятной ситуации\n/help - это сообщение\n' \
                        f'/settings - настройки профиля\n/goods - список товаров\n/cart - текущая корзина\n' \
                        f'/get_product - Поиск товара'
        if await is_admin(user_id):
            help_msg = help_msg + f'\n\n<b>Справка для администратора</b>:\n🔴 Для добавления товара воспользуйтесь ' \
                                  f'коммандой /goods и нажмите соответствующую кнопку.\n🔴 Для того, что бы ' \
                                  f'отредактировать товар или удалить, нужно открыть его. Это можно сделать найдя ' \
                                  f'его в списке товара (/goods) или воспользовавшись поиском (/get_product).'
        return help_msg

    async def profile(self, user_id: int) -> str:
        answer: str = await get_profile(user_id)
        return answer

    async def admin(self, user_id: int) -> str:
        answer: str = 'Ожидание ввода'
        await edit_last_bot_msg(user_id, bot_msg=edit_admin)
        return answer

    async def goods(self, user_id: int) -> str:
        if await is_admin(user_id):
            answer: str = 'Выберите вариант:'
        else:
            answer: str = 'Выберите фильтр'
        return answer

    async def cancel_msg(self, user_id) -> str:
        await edit_last_bot_msg(user_id)
        return 'Действие отменено'


async def answer_text(message: Message) -> Message:
    if await is_last_bot_message(message.from_user.id):
        answer: Message = await other_answer(message)
    else:
        answer: Message = await message.answer(text='Сообщение не распознано')
    return answer


async def callback(callback_query: CallbackQuery) -> Message:
    data: list = callback_query.data.split('-')
    if data[0] in edit:
        answer: Message = await callback_edit_profile(callback_query=callback_query)
    elif data[0] in order:
        answer: Message = await callback_order(callback_query=callback_query)
    elif data[0] in get_product:
        answer: Message = await callback_product(callback_query=callback_query)
    elif data[0] in prod[3]:
        answer: Message = await callback_filter(callback_query=callback_query)
    elif data[0] in prod[2]:
        answer: Message = await callback_edit_product(callback_query=callback_query)
    elif data[0] in prod[0]:
        answer: Message = await add_product(callback_query=callback_query)
    elif data[0] == 'no prod':
        answer: str = await StaticMessage().goods(callback_query.from_user.id)
        keyboard: InlineKeyboardMarkup = await InlineKeyboard().filter_product(callback_query.from_user.id)
        answer: Message = await callback_query.message.edit_text(text=answer, reply_markup=keyboard)


    # elif data[0] in prod[][]:
    #     answer: Message = await
    else:
        print(data)
        await callback_query.answer(text='Ничего не произошло, это info-кнопка')
        answer = 'Была нажата информативная кнопка'
    return answer
