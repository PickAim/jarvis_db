from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from jarvis_db.db_config import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    profit_tax = Column(Integer, nullable=False)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)


class Pay(Base):
    __tablename__ = 'pays'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    payment_date = Column(DateTime(), nullable=False, default=datetime.now)
    is_auto = Column(Boolean, nullable=False)
    payment_key = Column(String(255), nullable=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    niches = relationship('Niche', back_populates='category')


class Niche(Base):
    __tablename__ = 'niches'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    category_id = Column(Integer(), ForeignKey(
        f'{Category.__tablename__}.id'))
    category = relationship('Category', back_populates='niches')
    matketplace_commission = Column(Integer)
    partial_client_commission = Column(Integer)
    client_commission = Column(Integer)
    return_percent = Column(Integer)
    update_date = Column(DateTime(), default=datetime.now)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    country = Column(String(60), nullable=False)
    region = Column(String(60), nullable=False)
    street = Column(String(255), nullable=False)
    number = Column(String(60), nullable=False)
    corpus = Column(String(60), nullable=False)


class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    global_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    addresss_id = Column(Integer, ForeignKey(f'{Address.__tablename__}.id'))
    logistic_to_customer_commission = Column(Integer)
    logistic_from_customer_commission = Column(Integer)
    basic_storage_commission = Column(Integer)
    additional_storage_commission = Column(Integer)
    monopalette_storage_commission = Column(Integer)


class MarketPlace(Base):
    __tablename__ = 'marketplaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class MarketPlaceInfo(Base):
    __tablename__ = 'marketplace_info'
    id = Column(Integer, primary_key=True)
    marketplace_id = Column(Integer, ForeignKey(
        f'{MarketPlace.__tablename__}.id'))
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    api_key = Column(String(255))


class ProductCard(Base):
    __tablename__ = 'products_cards'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    article = Column(Integer, nullable=False)
    cost = Column(Integer)
    market_place_id = Column(Integer, ForeignKey(
        f'{MarketPlace.__tablename__}.id'))
    niche_id = Column(Integer(), ForeignKey(f'{Niche.__tablename__}.id'))


class ProductCostHistory(Base):
    __tablename__ = 'product_cost_histories'
    id = Column(Integer, primary_key=True)
    cost = Column(Integer(), nullable=False)
    date = Column(DateTime(), nullable=False, default=datetime.now)
    product_id = Column(Integer, ForeignKey(f'{ProductCard.__tablename__}.id'))


class StorageInfo(Base):
    __tablename__ = 'storage_info'
    id = Column(Integer, primary_key=True)
    product_card_id = Column(Integer, ForeignKey(
        f'{ProductCard.__tablename__}.id'))
    warehouse_id = Column(Integer, ForeignKey(f'{Warehouse.__tablename__}.id'))
    leftover = Column(Integer)


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    date = Column(DateTime(), default=datetime.now)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)


class FrequencyRequest(Base):
    __tablename__ = 'frequency_requests'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Request.__tablename__}.id'))
    search_str = Column(String(255))


class EconomyRequest(Base):
    __tablename__ = 'economy_requests'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Request.__tablename__}.id'))
    niche_id = Column(Integer, ForeignKey(f'{Niche.__tablename__}.id'))
    prime_cost = Column(Integer)
    transit_cost = Column(Integer)
    transit_count = Column(Integer)


class FrequencyResult(Base):
    __tablename__ = 'frequency_results'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Result.__tablename__}.id'))
    cost = Column(Integer)
    frequency = Column(Integer)


class EcomonyResult(Base):
    __tablename__ = 'ecomony_results'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Result.__tablename__}.id'))
    buy_cost = Column(Integer)
    pack_cost = Column(Integer)
    marketplace_commission = Column(Integer)
    logistic_price = Column(Integer)
    margin = Column(Integer)
    recomended_price = Column(Integer)
    transit_profit = Column(Integer)
    roi = Column(Integer)
    transit_margin_percent = Column(Integer)
