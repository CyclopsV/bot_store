import logging
from datetime import datetime
from decimal import Decimal
from os.path import abspath, dirname, join, isfile, getsize

from aiogram import types
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey, Table
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, Session

from config import Config

engine: Engine = create_engine(Config.URI_DB, echo=False)
metadata: MetaData = MetaData(bind=engine)
Base: DeclarativeMeta = declarative_base(metadata=metadata)
Session: Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'
    id: Integer = Column(Integer, primary_key=True)
    user_name: String = Column(String(50))
    name: String = Column(String(50))
    admin: Boolean = Column(Boolean, default=False)
    date_registration: DateTime = Column(DateTime, default=datetime.today())
    date_last_use: DateTime = Column(DateTime, default=datetime.today())
    last_bot_msg: String = Column(String(100))
    orders: list = relationship('Order', backref='user')

    def __init__(self, user: types.User):
        self.id = user.id
        self.user_name = user.username
        self.name = user.full_name

    def __repr__(self):
        u_name = f't.me/{self.user_name}'
        if self.user_name is None:
            u_name = f'tg://user?id={self.id}'
        return f'<User : {self.id}, {u_name}>'


order_product: Table = Table('order_product', metadata,
                             Column('order_id', Integer, ForeignKey('orders.id')),
                             Column('product_id', Integer, ForeignKey('products.id')))


class Product(Base):
    __tablename__ = 'products'
    id: Integer = Column(Integer, primary_key=True)
    name: String = Column(String(50))
    definition: String = Column(String(970))
    img: String = Column(String(105))
    available: Boolean = Column(Boolean, default=False)
    price: DECIMAL = DECIMAL(Decimal)
    date_create: DateTime = Column(DateTime, default=datetime.today())
    date_update: DateTime = Column(DateTime, default=datetime.today())

    # orders = relationship('Order', secondary=order_product, backref='products')

    def __repr__(self):
        return f'<Product : {self.id}, {self.name}>'


class Order(Base):
    __tablename__ = 'orders'
    id: Integer = Column(Integer, primary_key=True)
    status: Boolean = Column(Boolean, default=False)
    user_id: Integer = Column(Integer, ForeignKey('users.id'))
    user: User = relationship('User', backref='orders')

    # products = relationship('Product', secondary=order_product, backref='orders')

    def __repr__(self):
        return f'Cart : {self.id}, {self.user}, {self.status}>'


def create_db() -> None:
    path_db = join(abspath(dirname(dirname(__file__))), 'app.db')
    logging.info(f'Поиск базы данных ({path_db})')
    if not isfile(path_db):
        logging.info(f'Создание базы данных ({path_db})')
        metadata.create_all(engine)
        logging.info(f'База данных создана')
    else:
        logging.info(f'База данных существует (Размер: {getsize(path_db)} байт)')
    return
