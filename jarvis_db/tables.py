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

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, profit_tax={self.profit_tax!r})'


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'Account(id={self.id!r}, login={self.login!r}, password={self.password!r})'


class Pay(Base):
    __tablename__ = 'pays'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    payment_date = Column(DateTime(), nullable=False, default=datetime.now)
    is_auto = Column(Boolean, nullable=False)
    payment_key = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'Pay(id={self.id!r}, payment_date={self.payment_date!r}, is_auto={self.is_auto!r})'


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    niches = relationship('Niche', back_populates='category')

    def __repr__(self) -> str:
        return f'Category(id={self.id}, name={self.name!r})'


class Niche(Base):
    __tablename__ = 'niches'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    category_id = Column(Integer(), ForeignKey(
        f'{Category.__tablename__}.id'))
    category = relationship('Category', back_populates='niches')
    matketplace_commission = Column(Integer, nullable=False)
    partial_client_commission = Column(Integer, nullable=False)
    client_commission = Column(Integer, nullable=False)
    return_percent = Column(Integer, nullable=False)
    update_date = Column(DateTime(), nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f'Niche(id={self.id!r}, '
            f'name={self.name!r}, '
            f'matketplace_commission={self.matketplace_commission!r}, '
            f'partial_client_commission={self.partial_client_commission!r}, '
            f'client_commission={self.client_commission!r}, '
            f'return_percent={self.return_percent!r}, '
            f'update_date={self.update_date!r}'
            ')'
        )


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    country = Column(String(60), nullable=False)
    region = Column(String(60), nullable=False)
    street = Column(String(255), nullable=False)
    number = Column(String(60), nullable=False)
    corpus = Column(String(60), nullable=False)

    def __repr__(self) -> str:
        return (
            f'Address(id={self.id!r}, )'
            f'country={self.country!r}, '
            f'region={self.region!r}, '
            f'street={self.street!r}, '
            f'number={self.number!r}, '
            f'corpus={self.corpus!r}'
            ')'
        )


class Marketplace(Base):
    __tablename__ = 'marketplaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    warehouses = relationship('Warehouse', back_populates='owner')

    def __repr__(self) -> str:
        return f'Marketplace(id={self.id!r}, name={self.name!r})'


class MarketplaceInfo(Base):
    __tablename__ = 'marketplace_info'
    id = Column(Integer, primary_key=True)
    marketplace_id = Column(Integer, ForeignKey(
        f'{Marketplace.__tablename__}.id'), nullable=False)
    user_id = Column(Integer, ForeignKey(
        f'{User.__tablename__}.id'), nullable=False)
    api_key = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'MarketplaceInfo(id={self.id!r}, api_key={self.api_key!r})'


class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey(
        f'{Marketplace.__tablename__}.id'), nullable=False)
    owner = relationship('Marketplace', back_populates='warehouses')
    global_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    addresss_id = Column(Integer, ForeignKey(
        f'{Address.__tablename__}.id'), nullable=False)
    address = relationship('Address', uselist=False)
    logistic_to_customer_commission = Column(Integer, nullable=False)
    logistic_from_customer_commission = Column(Integer, nullable=False)
    basic_storage_commission = Column(Integer, nullable=False)
    additional_storage_commission = Column(Integer, nullable=False)
    monopalette_storage_commission = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f'Warehouse(id={self.id!r}, '
            f'global_id={self.global_id!r}, '
            f'type={self.type!r}, '
            f'name={self.name!r}, '
            f'logistic_to_customer_commission={self.logistic_to_customer_commission!r}, '
            f'logistic_from_customer_commission={self.logistic_from_customer_commission!r}, '
            f'basic_storage_commission={self.basic_storage_commission!r}, '
            f'additional_storage_commission={self.additional_storage_commission!r}, '
            f'monopalette_storage_commission={self.monopalette_storage_commission!r}'
            ')'
        )


class ProductCard(Base):
    __tablename__ = 'products_cards'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    article = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    market_place_id = Column(Integer, ForeignKey(
        f'{Marketplace.__tablename__}.id'))
    niche_id = Column(Integer(), ForeignKey(
        f'{Niche.__tablename__}.id'), nullable=False)

    def __repr__(self) -> str:
        return f'ProductCard(id={self.id!r}, name={self.name!r}, article={self.article!r}, cost={self.cost!r})'


class ProductCostHistory(Base):
    __tablename__ = 'product_cost_histories'
    id = Column(Integer, primary_key=True)
    cost = Column(Integer(), nullable=False)
    date = Column(DateTime(), nullable=False, default=datetime.now)
    product_id = Column(Integer, ForeignKey(
        f'{ProductCard.__tablename__}.id'), nullable=False)

    def __repr__(self) -> str:
        return f'ProductCostHistory(id={self.id!r}, cost={self.cost!r}, date={self.date!r})'


class StorageInfo(Base):
    __tablename__ = 'storage_info'
    id = Column(Integer, primary_key=True)
    product_card_id = Column(Integer, ForeignKey(
        f'{ProductCard.__tablename__}.id'))
    warehouse_id = Column(Integer, ForeignKey(f'{Warehouse.__tablename__}.id'))
    leftover = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'StorageInfo(id={self.id!r}, leftover={self.leftover!r})'


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    date = Column(DateTime(), nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return f'Request(id={self.id!r}, date={self.date!r})'


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f'Result(id={self.id!r})'


class FrequencyRequest(Base):
    __tablename__ = 'frequency_requests'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Request.__tablename__}.id'))
    search_str = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'FrequencyRequest(id={self.id!r}, search_str={self.search_str!r})'


class EconomyRequest(Base):
    __tablename__ = 'economy_requests'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Request.__tablename__}.id'))
    niche_id = Column(Integer, ForeignKey(f'{Niche.__tablename__}.id'))
    prime_cost = Column(Integer, nullable=False)
    transit_cost = Column(Integer, nullable=False)
    transit_count = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'EconomyRequest(id={self.id!r}, prime_cost={self.prime_cost!r}, transit_cost={self.transit_cost!r}, transit_count={self.transit_count!r})'


class FrequencyResult(Base):
    __tablename__ = 'frequency_results'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Result.__tablename__}.id'))
    cost = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'FrequencyResult(id={self.id!r}, cost={self.cost!r}, frequency={self.frequency!r})'


class EcomonyResult(Base):
    __tablename__ = 'ecomony_results'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(f'{Result.__tablename__}.id'))
    buy_cost = Column(Integer, nullable=False)
    pack_cost = Column(Integer, nullable=False)
    marketplace_commission = Column(Integer, nullable=False)
    logistic_price = Column(Integer, nullable=False)
    margin = Column(Integer, nullable=False)
    recomended_price = Column(Integer, nullable=False)
    transit_profit = Column(Integer, nullable=False)
    roi = Column(Integer, nullable=False)
    transit_margin_percent = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f'EcomonyResult(id={self.id!r}, '
            f'buy_cost={self.buy_cost!r}, '
            f'pack_cost={self.pack_cost!r}, '
            f'marketplace_commission={self.marketplace_commission!r}, '
            f'logistic_price={self.logistic_price!r}, '
            f'recomended_price={self.recomended_price!r}, '
            f'transit_profit={self.transit_profit!r}, '
            f'roi={self.roi!r}, '
            f'transit_margin_percent={self.transit_margin_percent!r}, '
        )
