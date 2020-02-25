from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from . import Base, metadata


class User(Base):
    __tablename__ = 'users'
    id: Integer = Column(Integer, primary_key=True)
    user_name: String = Column(String(50))
    name: String = Column(String(50))
    admin: bool = Column(bool, default=False)
    date_registration: DateTime = Column(DateTime, default=datetime.today())
    date_last_use: DateTime = Column(DateTime, default=datetime.today())
    last_bot_msg: String = Column(String(100))
    orders: list = relationship('Order', backref='user')

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
    available: bool = Column(bool, default=False)
    price: Decimal = Column(Decimal)
    date_create: DateTime = Column(DateTime, default=datetime.today())
    date_update: DateTime = Column(DateTime, default=datetime.today())
    orders: list = relationship('Order', secondary=order_product, backref='products')

    def __repr__(self):
        return f'<Product : {self.id}, {self.name}>'


class Order(Base):
    __tablename__ = 'orders'
    id: Integer = Column(Integer, primary_key=True)
    status: bool = Column(bool, default=False)
    user_id: Integer = Column(Integer, ForeignKey('users.id'))
    user: User = relationship('User', backref='orders')
    products: list = relationship('Product', secondary=order_product, backref='orders')

    def __repr__(self):
        return f'Cart : {self.id}, {self.user}, {self.status}>'
