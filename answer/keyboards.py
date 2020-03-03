from decimal import Decimal

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database.models import Session, Order, User, Product, engine, order_product
from .statiс import edit, prod, get_product


class Keyboard(ReplyKeyboardMarkup):
    _help_button: KeyboardButton = KeyboardButton('/help - 🆘 Справка')
    _settings_button: KeyboardButton = KeyboardButton('/settings - 📝 Настройки профиля')
    _goods_button: KeyboardButton = KeyboardButton('/goods - 📦 Список товаров')
    _cart_button: KeyboardButton = KeyboardButton('/cart - 🛒 Текущая корзина')
    _serch: KeyboardButton = KeyboardButton('/get_product - 🔍 Поиск товара')

    async def help(self) -> ReplyKeyboardMarkup:
        self.resize_keyboard = True
        return self.add(self._help_button)

    async def base(self) -> ReplyKeyboardMarkup:
        self.resize_keyboard = True
        self.row_width = 1
        self.add(self._help_button, self._settings_button, self._goods_button, self._cart_button, self._serch)
        return self


class InlineKeyboard(InlineKeyboardMarkup):

    async def profile(self, user_id: int, session: Session = Session()) -> InlineKeyboardMarkup:
        user: User = session.query(User).filter(User.id == user_id).first()
        edit_name: InlineKeyboardButton = InlineKeyboardButton(text='Изменить имя', callback_data=edit[0])
        if not user.name:
            edit_name.text = 'Добавить имя'
        self.add(edit_name)
        edit_location: InlineKeyboardButton = InlineKeyboardButton(text='Изменить город доставки',
                                                                   callback_data=edit[1])
        if not user.location:
            edit_location.text = 'Добавить город доставки'
        self.add(edit_location)
        edit_phone: InlineKeyboardButton = InlineKeyboardButton(text='Изменить номер телефона',
                                                                callback_data=edit[2])
        if not user.telephone:
            edit_phone.text = 'Добавить телефон'
        self.add(edit_phone)
        if len(user.orders) > 0:
            orders: list = session.query(Order).filter(Order.user == user).filter(Order.status == True).all()
            if len(orders) > 0:
                list_orders: InlineKeyboardButton = InlineKeyboardButton(text='Список выполненных заказов',
                                                                         callback_data=edit[0])
                self.add(list_orders)
            order: Order = session.query(Order).filter(Order.user == user).filter(Order.status == False).first()
            if order:
                new_order: InlineKeyboardButton = InlineKeyboardButton(text='Текущий заказ',
                                                                       callback_data=edit[1])
                self.add(new_order)
        return self

    async def order_list_button(self, orders: list, session: Session = Session()) -> InlineKeyboardMarkup:
        for order in orders:
            products: list = order.products
            session.query()
            money: Decimal = Decimal('0')
            for product in products:
                count_product: int = engine.connect().execute(select([order_product.c.count]).where(
                    (order_product.c.order_id == order.id) & (order_product.c.product_id == product.id)))[0]
                price: Decimal = Decimal(product.price) * Decimal(count_product)
                money = money + price
            self.add(InlineKeyboardButton(text=f'📅{order.date.strftime("%d.%m.%y")}💸{money}🛒{count_product}',
                                          callback_data=f'{edit["get_order"]}-{order.id}'))
        return self

    async def product(self, product_id: int, user_id: int, session: Session = Session()) -> InlineKeyboardMarkup:
        user: User = session.query(User).filter(User.id == user_id).first()
        order: Order = session.query(Order).filter(Order.user == user).filter(Order.status == False).first()
        product = session.query(Product).filter(Product.id == product_id).first()
        id_btn: InlineKeyboardButton = InlineKeyboardButton(text=f'ID: #⃣{product.id}', callback_data='None')
        count_product: int = 0
        if order:
            query = order_product.select(order_product.c.count).where(
                (order_product.c.order_id == order.id) & (order_product.c.product_id == product.id))
            count_product = engine.connect().execute(query).fetchall()[0][-1]
        count_btn: InlineKeyboardButton = InlineKeyboardButton(text=f'📦{count_product}', callback_data='None')
        self.add(id_btn, count_btn)
        self.add(InlineKeyboardButton(text=f'Цена: {product.price}', callback_data='None'))
        if product.available:
            self.add(InlineKeyboardButton(text='Добавить в корзину', callback_data=f'{prod[0]}-{product_id}'))
        else:
            self.add(InlineKeyboardButton(text='Товар недоступен для заказа', callback_data='None'))
        if order and (product in order.products):
            self.add(InlineKeyboardButton(text='Удалить из корзины', callback_data=f'{prod[1]}-{product_id}'))
        if user.admin:
            self.add(InlineKeyboardButton(text='Изменить название', callback_data=f'{prod[2][0]}-{product_id}'))
            self.add(InlineKeyboardButton(text='Изменить картинку', callback_data=f'{prod[2][1]}-{product_id}'))
            self.add(InlineKeyboardButton(text='Изменить описание', callback_data=f'{prod[2][2]}-{product_id}'))
            self.add(InlineKeyboardButton(text='Изменить цену', callback_data=f'{prod[2][3]}-{product_id}'))
            if product.available:
                self.add(
                    InlineKeyboardButton(text='Товар доступен (изменить?)', callback_data=f'{prod[2][4]}-{product_id}'))
            else:
                self.add(InlineKeyboardButton(text='Товар недоступен (изменить?)',
                                              callback_data=f'{prod[2][4]}-{product_id}'))
        return self

    async def filter_product(self, user_id: int, session: Session = Session()) -> InlineKeyboardMarkup:
        self.add(InlineKeyboardButton(text='Товары дешевле 5000', callback_data=f'{prod[3][0]}-0-90'))
        self.add(InlineKeyboardButton(text='Товары дороже 5000', callback_data=f'{prod[3][1]}-0-90'))
        user: User = session.query(User).filter(User.id == user_id).filter(User.admin == True).first()
        if user:
            self.add(InlineKeyboardButton(text='Добавить товар', callback_data=prod[3][2]))
        return self

    async def list_products(self, first: int, end: int, user_id: int, price: str,
                            session: Session = Session()) -> InlineKeyboardMarkup:
        user: User = session.query(User).filter(User.id == user_id).filter(User.admin == True).first()
        if user:
            if price == prod[3][0]:
                products = session.query(Product).filter((Product.price < '5000') | (Product.price == None)).order_by(
                    Product.name).all()
            else:
                products = session.query(Product).filter((Product.price >= '5000') | (Product.price == None)).order_by(
                    Product.name).all()
        else:
            if price == prod[3][0]:
                products = session.query(Product).filter(Product.price < '5000').filter(
                    Product.available == True).order_by(
                    Product.name).all()
            else:
                products = session.query(Product).filter(Product.price >= '5000').filter(
                    Product.available == True).order_by(Product.name).all()
        if first < 0:
            first = 0
            end = 90
        count_prod = len(products)
        products = products[first:end]
        if products:
            for product in products:
                self.add(InlineKeyboardButton(text=f'💸{product.price} 🛒{product.name}',
                                              callback_data=f'{get_product}-{product.id}'))
            back_btn: InlineKeyboardButton = InlineKeyboardButton(text='🔙',
                                                                  callback_data=f'{price}-{first - 91}-{first - 1}')
            next_btn: InlineKeyboardButton = InlineKeyboardButton(text='🔜',
                                                                  callback_data=f'{price}-{end + 1}-{end - 91}')
            if (first > 0) and (end < count_prod):
                self.add(back_btn, next_btn)
            elif (first == 0) and (end < count_prod):
                self.add(next_btn)
            elif (first > 0) and (end >= count_prod):
                self.add(back_btn)
        else:
            self.add(InlineKeyboardButton(text='Увы, товаров нет', callback_data='no prod'))
        return self
