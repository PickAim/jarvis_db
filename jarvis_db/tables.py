from datetime import datetime

from sqlalchemy import (Boolean, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jarvis_db.db_config import Base


class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'Account(id={self.id!r}, login={self.login!r}, password={self.password!r})'


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profit_tax: Mapped[int] = mapped_column(Integer, nullable=False)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Account.id), nullable=False)
    account: Mapped[Account] = relationship(Account, uselist=False)

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, profit_tax={self.profit_tax!r})'


class Pay(Base):
    __tablename__ = 'pays'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{User.__tablename__}.id'))
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow)
    is_auto: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payment_key: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'Pay(id={self.id!r}, payment_date={self.payment_date!r}, is_auto={self.is_auto!r})'


class Address(Base):
    __tablename__ = 'addresses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(60), nullable=False)
    region: Mapped[str] = mapped_column(String(60), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    number: Mapped[str] = mapped_column(String(60), nullable=False)
    corpus: Mapped[str] = mapped_column(String(60), nullable=False)

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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    warehouses: Mapped[list['Warehouse']] = relationship(
        'Warehouse', back_populates='owner')
    categories: Mapped[list['Category']] = relationship(
        'Category', back_populates='marketplace')

    def __repr__(self) -> str:
        return f'Marketplace(id={self.id!r}, name={self.name!r})'


class MarketplaceInfo(Base):
    __tablename__ = 'marketplace_info'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        f'{Marketplace.__tablename__}.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        f'{User.__tablename__}.id'), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'MarketplaceInfo(id={self.id!r}, api_key={self.api_key!r})'


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    niches: Mapped[list['Niche']] = relationship(
        'Niche', back_populates='category')
    marketplace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Marketplace.id), nullable=False)
    marketplace: Mapped[Marketplace] = relationship(
        Marketplace, back_populates='categories')

    __table_args__ = (UniqueConstraint(name, marketplace_id),)

    def __repr__(self) -> str:
        return f'Category(id={self.id}, name={self.name!r})'


class Niche(Base):
    __tablename__ = 'niches'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(
        Integer(), ForeignKey(Category.id))
    category: Mapped[Category] = relationship(
        'Category', back_populates='niches')
    marketplace_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    partial_client_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    client_commission: Mapped[int] = mapped_column(Integer, nullable=False)
    return_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    update_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow)
    products: Mapped[list['ProductCard']] = relationship(
        'ProductCard', back_populates='niche')

    __table_args__ = (UniqueConstraint(name, category_id),)

    def __repr__(self) -> str:
        return (
            f'Niche(id={self.id!r}, '
            f'name={self.name!r}, '
            f'marketplace_commission={self.marketplace_commission!r}, '
            f'partial_client_commission={self.partial_client_commission!r}, '
            f'client_commission={self.client_commission!r}, '
            f'return_percent={self.return_percent!r}, '
            f'update_date={self.update_date!r}'
            ')'
        )


class Warehouse(Base):
    __tablename__ = 'warehouses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Marketplace.id), nullable=False)
    owner: Mapped[Marketplace] = relationship(
        'Marketplace', back_populates='warehouses')
    global_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        f'{Address.__tablename__}.id'), nullable=False)
    address: Mapped[Address] = relationship('Address', uselist=False)
    basic_logistic_to_customer_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    additional_logistic_to_customer_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    logistic_from_customer_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    basic_storage_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    additional_storage_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    monopalette_storage_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f'Warehouse(id={self.id!r}, '
            f'global_id={self.global_id!r}, '
            f'type={self.type!r}, '
            f'name={self.name!r}, '
            f'logistic_to_customer_commission={self.basic_logistic_to_customer_commission!r}, '
            f'logistic_from_customer_commission={self.logistic_from_customer_commission!r}, '
            f'basic_storage_commission={self.basic_storage_commission!r}, '
            f'additional_storage_commission={self.additional_storage_commission!r}, '
            f'monopalette_storage_commission={self.monopalette_storage_commission!r}'
            ')'
        )


class ProductCard(Base):
    __tablename__ = 'products_cards'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    article: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    niche_id: Mapped[int] = mapped_column(Integer(), ForeignKey(
        f'{Niche.__tablename__}.id'), nullable=False)
    niche: Mapped[Niche] = relationship('Niche', back_populates='products')

    __table_args__ = (UniqueConstraint(name, article, niche_id),)

    def __repr__(self) -> str:
        return f'ProductCard(id={self.id!r}, name={self.name!r}, article={self.article!r}, cost={self.cost!r})'


class ProductCostHistory(Base):
    __tablename__ = 'product_cost_histories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost: Mapped[int] = mapped_column(Integer(), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        f'{ProductCard.__tablename__}.id'), nullable=False)
    product: Mapped[ProductCard] = relationship('ProductCard', uselist=False)

    def __repr__(self) -> str:
        return f'ProductCostHistory(id={self.id!r}, cost={self.cost!r}, date={self.date!r})'


class StorageInfo(Base):
    __tablename__ = 'storage_info'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_card_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        f'{ProductCard.__tablename__}.id'))
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Warehouse.__tablename__}.id'))
    leftover: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'StorageInfo(id={self.id!r}, leftover={self.leftover!r})'


class Request(Base):
    __tablename__ = 'requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{User.__tablename__}.id'))
    date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'Request(id={self.id!r}, date={self.date!r})'


class Result(Base):
    __tablename__ = 'results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f'Result(id={self.id!r})'


class FrequencyRequest(Base):
    __tablename__ = 'frequency_requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Request.__tablename__}.id'))
    search_str: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'FrequencyRequest(id={self.id!r}, search_str={self.search_str!r})'


class EconomyRequest(Base):
    __tablename__ = 'economy_requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Request.__tablename__}.id'))
    niche_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Niche.__tablename__}.id'))
    prime_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_count: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'EconomyRequest(id={self.id!r}, prime_cost={self.prime_cost!r}, transit_cost={self.transit_cost!r}, transit_count={self.transit_count!r})'


class FrequencyResult(Base):
    __tablename__ = 'frequency_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Result.__tablename__}.id'))
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'FrequencyResult(id={self.id!r}, cost={self.cost!r}, frequency={self.frequency!r})'


class EconomyResult(Base):
    __tablename__ = 'economy_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f'{Result.__tablename__}.id'))
    buy_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    pack_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    marketplace_commission: Mapped[int] = mapped_column(
        Integer, nullable=False)
    logistic_price: Mapped[int] = mapped_column(Integer, nullable=False)
    margin: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_price: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_profit: Mapped[int] = mapped_column(Integer, nullable=False)
    roi: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_margin_percent: Mapped[int] = mapped_column(
        Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f'EconomyResult(id={self.id!r}, '
            f'buy_cost={self.buy_cost!r}, '
            f'pack_cost={self.pack_cost!r}, '
            f'marketplace_commission={self.marketplace_commission!r}, '
            f'logistic_price={self.logistic_price!r}, '
            f'recommended_price={self.recommended_price!r}, '
            f'transit_profit={self.transit_profit!r}, '
            f'roi={self.roi!r}, '
            f'transit_margin_percent={self.transit_margin_percent!r}, '
        )
