import logging
from decimal import Decimal

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config.secret import ADMIN_PSW
from database import Session
from database.models import User, Order, Product, order_product, engine
from .keyboards import InlineKeyboard
from .statiс import edit_admin, edit, prod


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
            print(message.photo[-1].file_id)
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
            price: str = str(round(float(text), 2))
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
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
    for product in order.products:
        price = price + Decimal(product.price)
        keyboard.add(
            InlineKeyboardButton(text=f'{product.name}', callback_data=f'{edit["get_product"]}-{product.id}'))
    answer: str = f'Ваш заказ: #⃣{order.id}\nПозиций: {len(order.products)}\nИтоговая цена:{price}'
    if order.status == True:
        answer = answer + f'\nЗавершен: {order.date.strftime("%d.%m.%y")}'
    if callback_query:
        return await callback_query.message.edit_text(text=answer, reply_markup=keyboard)
    else:
        return await message.answer(text=answer, reply_markup=keyboard)


async def callback_order(callback_query: CallbackQuery, session: Session = Session()) -> Message:
    if callback_query.data == edit['list_orders']:
        orders: list = session.query(Order).filter(Order.user_id == callback_query.from_user.id).filter(
            Order.status == True).order_by(Order.date).all()[0:99]
        keyboard: InlineKeyboardMarkup = await InlineKeyboard().order_list_button(orders)
        return await callback_query.message.edit_text(text=f'У вас {len(orders)} закрытых заказов',
                                                      reply_markup=keyboard)
    elif callback_query.data == edit['new_order']:
        return await get_order(callback_query=callback_query)
    elif edit['get_order'] in callback_query.data:
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
            answer = await callback_query.message.answer_photo(photo=product.img, caption=answer, reply_markup=keyboard)
            await callback_query.message.delete()
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


async def add_product(callback_query: CallbackQuery, session: Session = Session()):
    order: Order = session.query(Order).filter(Order.user_id == callback_query.from_user.id).filter(
        Order.status == False).first()
    if not order:
        order = Order(user_id=callback_query.from_user.id)
        session.add(order)
        # session.commit()
        # session = Session()
        # order: Order = session.query(Order).filter(Order.user_id == callback_query.from_user.id).filter(
        #     Order.status == False).first()
    product_id: int = int(callback_query.message.reply_markup.inline_keyboard[0][0].text.split('#⃣')[1])
    product: Product = session.query(Product).filter(Product.id == product_id).first()
    if product in order.products:
        query = order_product.select(order_product.c.count).where((order_product.c.order_id == order.id) & (
                    order_product.c.product_id == product.id))

        count_product: int = engine.connect().execute(query).fetchall()[0][-1]
        engine.connect().execute(
            order_product.update().values(count=count_product + 1).where((order_product.c.order_id == order.id) & (
                    order_product.c.product_id == product.id)))
    else:
        order.products = order.products + [product]
    session.commit()
    return await callback_product(callback_query=callback_query)
