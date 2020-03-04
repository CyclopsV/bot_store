import logging
from datetime import datetime
from decimal import Decimal

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from config.secret import ADMIN_PSW
from database import Session
from database.models import User, Order, Product, order_product, engine
from .keyboards import InlineKeyboard
from .statiс import edit_admin, edit, prod, order_com, get_product, buy, check, search


async def is_user(user_id: int, session: Session = Session()) -> bool:
    user: User = session.query(User).filter(User.id == user_id).first()
    return True if user else False


async def is_admin(user_id: int, session: Session = Session()) -> bool:
    user: User = session.query(User).filter(User.id == user_id).filter(User.admin == True).first()
    return True if user else False


async def is_last_bot_message(user_id: int, session: Session = Session()):
    user: User = session.query(User).filter(User.id == user_id).filter(User.last_bot_msg != None).first()
    return True if user else False


async def get_profile(user_id: int, session: Session = Session()) -> str:
    user: User = session.query(User).filter(User.id == user_id).first()
    orders: Order = session.query(Order).filter(Order.user == user).filter(Order.status == True).all()
    profile = f'Имя: {user.name} ({user.id})\n' \
              f'Имя пользователя: @{user.user_name}\n' \
              f'Город доставки: {user.location}\n' \
              f'Телефон: {user.telephone}\n' \
              f'Дата регистрации: {user.date_registration.strftime("%d.%m.%Y")}\n' \
              f'Количество выполненных заказов: {len(orders)}'
    if user.admin:
        profile = '<b>Вы администратор.</b>\n\n' + profile
    return profile


async def edit_last_bot_msg(user_id: int, bot_msg: str = None, session: Session = Session()) -> None:
    user: User = session.query(User).filter(User.id == user_id).first()
    user.last_bot_msg = bot_msg
    session.commit()


async def other_answer(message: Message, session: Session = Session()):
    user: User = session.query(User).filter(User.id == message.from_user.id).first()
    bot_message = user.last_bot_msg.split('-')

    if bot_message[0] == edit_admin:
        if message.text == ADMIN_PSW:
            user.admin = True
            logging.info(f'Пользователь {user} стал администратором')
            session.commit()
            await edit_last_bot_msg(message.from_user.id)
            return await message.answer(
                'Вы стали администратором!\nВоспользуйтесь коммандой /help для получения справки')
        else:
            logging.warning(f'Пользователь {user} ввел неверный пароль')
            await edit_last_bot_msg(user.id)
            return await message.answer('Поздравляю... Ничего не произошло...')
    elif (bot_message[0] == prod[3][2]) or (bot_message[0] == prod[2][0]):
        if len(message.text) < 50:
            if bot_message[0] == prod[3][2]:
                product: Product = Product(message.text)
                session.add(product)
                logging.info(f'Создан товар {product}, пользователем {user}')
            else:
                product: Product = session.query(Product).filter(Product.id == bot_message[1]).first()
                product.name = message.text
            user.last_bot_msg = None
            session.commit()
            await edit_last_bot_msg(message.from_user.id)
            return await callback_product(message=message, product_id=product.id)
        else:
            return await message.answer(f'Название товара должно быть короче 50 символов\nВаше название содержит '
                                        f'{len(message.text)} символов\n\nДля отмены создания используйте комманду '
                                        f'/cancel')
    elif bot_message[0] == prod[2][1]:
        if message.photo:
            product: Product = session.query(Product).filter(Product.id == bot_message[1]).first()
            product.img = message.photo[-1].file_id
            session.commit()
            await edit_last_bot_msg(message.from_user.id)
            return await callback_product(message=message, product_id=product.id)
        else:
            return await message.answer('Тип файла не поддерживается, отправте изображение')
    elif bot_message[0] == prod[2][2]:
        if len(message.text) < 970:
            product: Product = session.query(Product).filter(Product.id == bot_message[1]).first()
            product.definition = message.text
            session.commit()
            await edit_last_bot_msg(message.from_user.id)
            return await callback_product(message=message, product_id=product.id)
        else:
            return await message.answer(f'Описание товара должно быть короче 970 символов\nВаше название содержит '
                                        f'{len(message.text)} символов\n\nДля отмены создания используйте комманду '
                                        f'/cancel')
    elif bot_message[0] == prod[2][3]:
        text: str = message.text.replace(' ', '').replace(',', '.')
        try:
            price: int = int(float(text) * 100)
        except ValueError:
            return await message.answer(f'Не верное значение\nВы ввели: {text}\n\nДля отмены ввода /cancel')
        product: Product = session.query(Product).filter(Product.id == bot_message[1]).first()
        product.price = price
        session.commit()
        await edit_last_bot_msg(message.from_user.id)
        return await callback_product(message=message, product_id=product.id)
    elif bot_message[0] in edit:
        if bot_message[0] == edit[0]:
            if len(message.text) < 50:
                user.name = message.text
            else:
                return await message.answer(f'Длина имени должа быть меньше 50 символов\n\nВаше сообщение содержит '
                                            f'{len(message.text)} символов')
        elif bot_message[0] == edit[1]:
            if len(message.text) < 100:
                user.location = message.text
            else:
                return await message.answer(f'Длина адреса должа быть меньше 100 символов\n\nВаше сообщение содержит '
                                            f'{len(message.text)} символов')
        elif bot_message[0] == edit[2]:
            if len(message.text) < 25:
                user.telephone = message.text
            else:
                return await message.answer(f'Длина телефона должа быть меньше 25 символов\n\nВаше сообщение содержит '
                                            f'{len(message.text)} символов')
        session.commit()
        profile: str = await get_profile(user.id)
        keyboard: InlineKeyboardMarkup = await InlineKeyboard().profile(user.id)
        return await message.answer(text=profile, reply_markup=keyboard)
    elif bot_message[0] == search:
        products: list = session.query(Product).filter(Product.id.ilike(f'%{message.text}%')).all()
        products_list = []
        for product in products:
            products_list.append(product)
        products: list = session.query(Product).filter(Product.name.ilike(f'%{message.text}%')).all()
        for product in products:
            if product not in products_list:
                products_list.append(product)
        products: list = session.query(Product).filter(Product.definition.ilike(f'%{message.text}%')).all()
        for product in products:
            if product not in products_list:
                products_list.append(product)
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
        for product in products_list:
            status = '✔️' if product.available else '❌'
            keyboard.add(
                InlineKeyboardButton(text=f'{status} {product.name}', callback_data=f'{get_product}-{product.id}'))
        await edit_last_bot_msg(message.from_user.id)
        return await message.answer('Результаты поиска по вашему запросу:', reply_markup=keyboard)
    else:
        return await message.answer(
            'Сообщение не распознано\n\nПожалуйста, воспользуйтесь командой /cancel и попробуйте снова')


async def callback_edit_profile(callback_query: CallbackQuery, session: Session = Session()) -> Message:
    user: User = session.query(User).filter(User.id == callback_query.from_user.id).first()
    await edit_last_bot_msg(user.id, bot_msg=callback_query.data)
    if callback_query.data == edit[0]:
        answer: str = 'Как к вам обращаться?'
        await callback_query.answer('Отправьте свое имя')
    elif callback_query.data == edit[1]:
        answer: str = 'Отправьте название города в который отправлять товары'
        await callback_query.answer('Отправьте адрес доставки')
    elif callback_query.data == edit[2]:
        answer: str = 'Отправьте номер телефона, по которому можно с вами связаться'
        await callback_query.answer('Отправьте номер телефона (+7 9** *** ** **)')
    return await callback_query.message.edit_text(text=answer)


async def get_order(callback_query: CallbackQuery = None, message: Message = None, order_id: int = None,
                    session: Session = Session()) -> Message:
    if callback_query:
        user_id = callback_query.from_user.id
    else:
        user_id = message.from_user.id
    if order_id:
        order: Order = session.query(Order).filter(Order.id == order_id).first()
    else:
        order: Order = session.query(Order).filter(Order.user_id == user_id).filter(Order.status == False).first()
    price: Decimal = Decimal('0')
    cp = 0
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
    for product in order.products:
        query = order_product.select(order_product.c.count).where((order_product.c.order_id == order.id) & (
                order_product.c.product_id == product.id))
        count_product: int = engine.connect().execute(query).fetchall()
        if count_product:
            count_product = count_product[0][-1]
        else:
            count_product = 0
        price = price + Decimal(f'{round(product.price / 100, 2)}') * count_product
        cp = cp + count_product
        keyboard.add(
            InlineKeyboardButton(text=f'{product.name}', callback_data=f'{get_product}-{product.id}'))
    answer: str = f'Ваш заказ: #⃣{order.id}\nПозиций: {len(order.products)} ({cp})\nИтоговая цена: {price}'
    if order.status == True:
        answer = answer + f'\nЗавершен: {order.date.strftime("%d.%m.%y")}'
    else:
        if len(order.products) > 0:
            keyboard.add(InlineKeyboardButton(text='Заказать', callback_data=f'{buy}-{order.id}'))
    if callback_query:
        return await callback_query.message.edit_text(text=answer, reply_markup=keyboard)
    else:
        return await message.answer(text=answer, reply_markup=keyboard)


async def callback_order(callback_query: CallbackQuery, session: Session = Session()) -> Message:
    if callback_query.data == order_com[0]:
        orders: list = session.query(Order).filter(Order.user_id == callback_query.from_user.id).filter(
            Order.status == True).order_by(Order.date).all()[0:99]
        keyboard: InlineKeyboardMarkup = await InlineKeyboard().order_list_button(orders)
        return await callback_query.message.edit_text(text=f'У вас {len(orders)} закрытых заказов',
                                                      reply_markup=keyboard)
    elif callback_query.data == order_com[1]:
        return await get_order(callback_query=callback_query)
    elif order_com[2] in callback_query.data:
        data = callback_query.data.split('-')[1]
        return await get_order(order_id=data)


async def callback_product(callback_query: CallbackQuery = None, message: Message = None, product_id: int = None,
                           session: Session = Session()) -> Message:
    if callback_query:
        product_id = callback_query.data.split('-')[1]
        user_id: int = callback_query.from_user.id
    else:
        user_id: int = message.from_user.id
    product = session.query(Product).filter(Product.id == product_id).first()
    answer: str = f'{product.name}\n\n{product.definition}'
    keyboard: InlineKeyboardMarkup = await InlineKeyboard().product(product_id, user_id)
    if callback_query:
        await callback_query.answer(text='Открытие продукта')
        if product.img:
            answer: Message = await callback_query.message.answer_photo(photo=product.img, caption=answer,
                                                                        reply_markup=keyboard)
            await callback_query.message.delete()
        else:
            answer: Message = await callback_query.message.edit_text(text=answer, reply_markup=keyboard)
        return answer
    else:
        if product.img:
            answer: Message = await message.answer_photo(photo=product.img, caption=answer, reply_markup=keyboard)
        else:
            answer: Message = await message.answer(text=answer, reply_markup=keyboard)
        return answer


async def callback_filter(callback_query: CallbackQuery, session: Session = Session()) -> Message:
    data = callback_query.data.split('-')
    if data[0] == prod[3][2]:
        user: User = session.query(User).filter(User.id == callback_query.from_user.id).first()
        user.last_bot_msg = data[0]
        answer: Message = await callback_query.message.edit_text('Отправьте название продукта')
        await callback_query.answer('Создание товара')
    elif (data[0] == prod[3][0]) or (data[0] == prod[3][1]):
        if len(data) == 1:
            data[1] = 0
            data[2] = 90
        if len(data) == 3:
            if data[0] == prod[3][0]:
                keyboard: InlineKeyboardMarkup = await InlineKeyboard().list_products(first=int(data[1]),
                                                                                      end=int(data[2]),
                                                                                      price=prod[3][0],
                                                                                      user_id=callback_query.from_user.id)
                await callback_query.answer('Открытие списка товаров дешевле 5000')
            elif data[0] == prod[3][1]:
                keyboard: InlineKeyboardMarkup = await InlineKeyboard().list_products(first=int(data[1]),
                                                                                      end=int(data[2]),
                                                                                      price=prod[3][1],
                                                                                      user_id=callback_query.from_user.id)
                await callback_query.answer('Открытие списка товаров дороже 5000')
        answer: Message = await callback_query.message.edit_text(text='Список товаров', reply_markup=keyboard)
    session.commit()
    return answer


async def callback_edit_product(callback_query: CallbackQuery, session: Session = Session()) -> Message or str:
    user: User = session.query(User).filter(User.id == callback_query.from_user.id).filter(User.admin == True).first()
    if not user:
        logging.warning(f'Дыра безопасности. Пользователь {user} получил доступ к редактированию продукта')
        return await callback_query.message.edit_text(
            text='Как у вас это сообщение оказалось? Вы не можете пользоваться этим функционалом')
    data: str = callback_query.data.split('-')
    product_id: int = int(callback_query.message.reply_markup.inline_keyboard[0][0].text.split('#⃣')[1])
    answer: Message
    if data[0] == prod[2][0]:
        await callback_query.answer('Отправьте название')
        if callback_query.message.photo:
            answer = await callback_query.message.edit_caption('Отправьте название товара')
        else:
            answer = await callback_query.message.edit_text('Отправьте название товара')
    elif data[0] == prod[2][1]:
        await callback_query.answer('Отправьте изображение')
        if callback_query.message.photo:
            answer = await callback_query.message.edit_caption('Отправьте иллюстрацию для товара')
        else:
            answer = await callback_query.message.edit_text('Отправьте иллюстрацию для товара')
    elif data[0] == prod[2][2]:
        await callback_query.answer('Отправьте описание товара')
        if callback_query.message.photo:
            answer = await callback_query.message.edit_caption('Отправьте описание товара')
        else:
            answer = await callback_query.message.edit_text('Отправьте описание товара')
    elif data[0] == prod[2][3]:
        await callback_query.answer('Отправьте цену')
        if callback_query.message.photo:
            answer = await callback_query.message.edit_caption(
                'Отправьте цену товара\n\nИзбегайте дробных(0.5) цен, при их подсчете может возникнуть погрешность')
        else:
            answer = await callback_query.message.edit_text(
                'Отправьте цену товара\n\nИзбегайте дробных(0.5) цен, при их подсчете может возникнуть погрешность')
    elif data[0] == prod[2][4]:
        product: Product = session.query(Product).filter(Product.id == product_id).first()
        if product.price:
            product.available = not product.available
            session.commit()
            answer = await callback_product(callback_query)
        else:
            await callback_query.answer('У товара нет цены')
            return 'Попытка выложить товар без цены'
    if data[0] != prod[2][4]:
        user.last_bot_msg = f'{data[0]}-{product_id}'
        session.commit()
    return answer


async def add_product(callback_query: CallbackQuery, n: int, session: Session = Session()):
    order: Order = session.query(Order).filter(Order.user_id == callback_query.from_user.id).filter(
        Order.status == False).first()
    if not order:
        order = Order(user_id=callback_query.from_user.id)
        session.add(order)
    product_id: int = int(callback_query.message.reply_markup.inline_keyboard[0][0].text.split('#⃣')[1])
    product: Product = session.query(Product).filter(Product.id == product_id).first()
    if product in order.products:
        query = order_product.select(order_product.c.count).where((order_product.c.order_id == order.id) & (
                order_product.c.product_id == product.id))
        count_product: int = engine.connect().execute(query).fetchall()
        if count_product:
            count_product = count_product[0][-1]
        if (count_product == 1) and (n == -1):
            engine.connect().execute(order_product.delete().where((order_product.c.order_id == order.id) & (
                    order_product.c.product_id == product.id)))
            await callback_query.answer('Товар удален из заказа')
        else:
            engine.connect().execute(
                order_product.update().values(count=count_product + n).where((order_product.c.order_id == order.id) & (
                        order_product.c.product_id == product.id)))
            if n > 0:
                await callback_query.answer('Товар добавлен в заказ')
            else:
                await callback_query.answer('Часть товара (-1шт) удалена из заказа')
    else:
        order.products = order.products + [product]
        await callback_query.answer('Товар добавлен в заказ')
    session.commit()
    return await callback_product(callback_query=callback_query)


async def buy_order(callback_query: CallbackQuery, session: Session = Session()):
    user: User = session.query(User).filter(User.id == callback_query.from_user.id).first()
    order_id: int = int(callback_query.data.split('-')[1])
    order: Order = session.query(Order).filter(Order.id == order_id).first()
    order_price = 0
    products_text: str = ''
    for product in order.products:
        query = order_product.select(order_product.c.count).where((order_product.c.order_id == order.id) & (
                order_product.c.product_id == product.id))
        count_product: int = engine.connect().execute(query).fetchall()[0][-1]
        order_price = order_price + Decimal(f'{round(product.price / 100, 2)}') * count_product
        product_text: str = f'⭕<b>#p_{product.id}</b> 💲{product.price / 100} * {count_product}\n<i>{product.name}</i>\n\n'
        products_text = products_text + product_text
    answer_text = f'Заказ: #o_{order.id}\nЗаказчик: <a href = "tg://user?id={user.id}">{user.name}</a> ' \
                  f'(@{user.user_name})\nДоставка: {user.location}\n\n<b>Список товаров</b>:\n' + products_text + \
                  f'Сумма заказа: {order_price}\n\n(‼️После подтверждения заказа, пользователь не сможет его ' \
                  f'редактировать. Но будет отправлено уведомление о подтверждении заказа)'
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        InlineKeyboardButton('Подтвердить заказ', callback_data=f'{check}-{product.id}'))
    admins: list = session.query(User).filter(User.admin == True).all()
    log: str = f'Отправка заказа ({order}) администраторам:\n'
    for admin in admins:
        admin_msg: Message = await Config.bot.send_message(chat_id=admin.id, text=answer_text, reply_markup=keyboard)
        log = log + f'{admin} - > {admin_msg}\n'
    logging.info(log)
    await callback_query.answer('Заказ отправлен на обработку')
    return await callback_query.message.edit_text(
        'Ваш заказ отправлен администраторам, дождитесь подтверждения. (Вам могут написать, для уточнения деталей)')


async def check_order(callback_query: CallbackQuery, session: Session = Session()):
    order_id: int = int(callback_query.data.split('-')[1])
    order: Order = session.query(Order).filter(Order.id == order_id).first()
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        InlineKeyboardButton(f'Заказ подтвержден {order.date.strftime("%d.%m.%Y %H:%M")}', callback_data='None'))
    if order.status == False:
        order.status = True
        order.date = datetime.today()
        keyboard = InlineKeyboardMarkup(
            InlineKeyboardButton(f'Заказ подтвержден {order.date.strftime("%d.%m.%Y %H:%M")}', callback_data='None'))
    else:
        await callback_query.answer(f'Заказ уже был подтвержден ({order.date.strftime("%d.%m.%Y %H:%M")})')
        return await callback_query.message.edit_reply_markup(keyboard)
    await callback_query.answer('Заказ подтвержден')
    await callback_query.message.edit_reply_markup(keyboard)
    user: User = order.user
    keyboard = InlineKeyboard().add(InlineKeyboardButton(text='Перейти к заказу', callback_data=order_com[2]))
    return await Config.bot.send_message(user.id, text=f'Ваш заказ #{order.id} подтвержден', reply_markup=keyboard)
