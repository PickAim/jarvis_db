from datetime import datetime

from jorm.market.person import UserPrivilege
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jarvis_db.db_config import Base


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    email: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="account",
        uselist=False,
        cascade="delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Account(id={self.id!r}, login={self.phone!r}, password={self.password!r})"
        )


class UserToProduct(Base):
    __tablename__ = "users_to_products"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product_cards.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )


class UserToWarehouse(Base):
    __tablename__ = "users_to_warehouses"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"), primary_key=True, unique=True
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profit_tax: Mapped[int] = mapped_column(Integer, nullable=False)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Account.id, ondelete="CASCADE"), nullable=False
    )
    account: Mapped[Account] = relationship(
        Account, uselist=False, back_populates="user"
    )
    status: Mapped[UserPrivilege]
    token_set: Mapped["TokenSet"] = relationship(
        "TokenSet",
        back_populates="user",
        uselist=False,
        cascade="delete",
        passive_deletes=True,
    )
    marketplace_api_keys: Mapped[list["MarketplaceApiKey"]] = relationship(
        "MarketplaceApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    pays: Mapped[list["Pay"]] = relationship(
        "Pay",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    products: Mapped[list["ProductCard"]] = relationship(
        secondary=UserToProduct.__table__
    )
    warehouses: Mapped[list["Warehouse"]] = relationship(
        secondary=UserToWarehouse.__table__
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, profit_tax={self.profit_tax!r})"
        )


class TokenSet(Base):
    __tablename__ = "token_info"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access_token: Mapped[str] = mapped_column(String(512), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False)
    fingerprint_token: Mapped[str] = mapped_column(String(512), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship(User, uselist=False, back_populates="token_set")

    __table_args__ = (UniqueConstraint(user_id, refresh_token, fingerprint_token),)

    def __repr__(self) -> str:
        return (
            f"TokenInfo(id={self.id!r}, "
            f"access_token={self.access_token!r}, "
            f"refresh_token={self.refresh_token!r}, "
            f"fingerprint_token={self.fingerprint_token!r})"
            ")"
        )


class Pay(Base):
    __tablename__ = "pays"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship(User, back_populates="pays")
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow
    )
    is_auto: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payment_key: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return (
            f"Pay(id={self.id!r}, "
            "payment_date={self.payment_date!r}, "
            "is_auto={self.is_auto!r})"
        )


class SubscriptionGroupType(Base):
    __tablename__ = "subscription_group_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max: Mapped[int] = mapped_column(Integer, nullable=False)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    price_per_month: Mapped[int] = mapped_column(Integer, nullable=False)
    group_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(SubscriptionGroupType.id, ondelete="CASCADE"),
        nullable=False,
    )
    group_type: Mapped[SubscriptionGroupType] = relationship(SubscriptionGroupType)


subscription_groups = Table(
    "subscription_groups",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey(User.id, ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    ),
    Column(
        "subscription_id",
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(SubscriptionPlan.id, ondelete="CASCADE"), nullable=False
    )
    plan: Mapped[SubscriptionPlan] = relationship(SubscriptionPlan)
    valid_to: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    users: Mapped[list["User"]] = relationship(secondary=subscription_groups)
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    admin: Mapped[User] = relationship(User)


class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(60), nullable=False)
    region: Mapped[str] = mapped_column(String(60), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    number: Mapped[str] = mapped_column(String(60), nullable=False)
    corpus: Mapped[str] = mapped_column(String(60), nullable=False)
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        back_populates="address",
        uselist=False,
        cascade="delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Address(id={self.id!r}, )"
            f"country={self.country!r}, "
            f"region={self.region!r}, "
            f"street={self.street!r}, "
            f"number={self.number!r}, "
            f"corpus={self.corpus!r}"
            ")"
        )


class Marketplace(Base):
    __tablename__ = "marketplaces"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    api_keys: Mapped[list["MarketplaceApiKey"]] = relationship(
        "MarketplaceApiKey",
        back_populates="marketplace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    warehouses: Mapped[list["Warehouse"]] = relationship(
        "Warehouse",
        back_populates="marketplace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="marketplace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    economy_constants: Mapped["EconomyConstants"] = relationship(
        "EconomyConstants",
        back_populates="marketplace",
        cascade="delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Marketplace(id={self.id!r}, name={self.name!r})"


class EconomyConstants(Base):
    __tablename__ = "economy_constants"
    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey(Marketplace.id, ondelete="CASCADE"), primary_key=True
    )
    marketplace: Mapped[Marketplace] = relationship(
        Marketplace, back_populates="economy_constants"
    )
    max_mass: Mapped[int] = mapped_column(Integer, nullable=False)
    max_side_sum: Mapped[int] = mapped_column(Integer, nullable=False)
    max_side_length: Mapped[int] = mapped_column(Integer, nullable=False)
    max_standard_volume_in_liters: Mapped[int] = mapped_column(Integer, nullable=False)
    return_price: Mapped[int] = mapped_column(Integer, nullable=False)
    oversize_logistic_price: Mapped[int] = mapped_column(Integer, nullable=False)
    oversize_storage_price: Mapped[int] = mapped_column(Integer, nullable=False)
    standard_warehouse_logistic_price: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    standard_warehouse_storage_price: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    nds_tax: Mapped[int] = mapped_column(Integer, nullable=False)
    commercial_tax: Mapped[int] = mapped_column(Integer, nullable=False)
    self_employed_tax: Mapped[int] = mapped_column(Integer, nullable=False)


class MarketplaceApiKey(Base):
    __tablename__ = "marketplace_api_keys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Marketplace.id, ondelete="CASCADE"), nullable=False
    )
    marketplace: Mapped[Marketplace] = relationship(
        Marketplace, back_populates="api_keys"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship(User, back_populates="marketplace_api_keys")
    api_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    __table_args__ = (UniqueConstraint(user_id, marketplace_id),)

    def __repr__(self) -> str:
        return (
            f"MarketplaceApiKey(id={self.id!r},"
            f"marketplace_id={self.marketplace_id!r},"
            f"user_id={self.user_id!r},"
            f"api_key={self.api_key!r})"
        )


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    marketplace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Marketplace.id, ondelete="CASCADE"), nullable=False
    )
    marketplace: Mapped[Marketplace] = relationship(
        Marketplace, back_populates="categories"
    )
    niches: Mapped[list["Niche"]] = relationship(
        "Niche",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint(name, marketplace_id),)

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r})"


class Niche(Base):
    __tablename__ = "niches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Category.id, ondelete="CASCADE")
    )
    category: Mapped[Category] = relationship("Category", back_populates="niches")
    marketplace_commission: Mapped[int] = mapped_column(Integer, nullable=False)
    partial_client_commission: Mapped[int] = mapped_column(Integer, nullable=False)
    client_commission: Mapped[int] = mapped_column(Integer, nullable=False)
    return_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    update_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow
    )
    products: Mapped[list["ProductCard"]] = relationship(
        "ProductCard",
        back_populates="niche",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint(name, category_id),)

    def __repr__(self) -> str:
        return (
            f"Niche(id={self.id!r}, "
            f"name={self.name!r}, "
            f"marketplace_commission={self.marketplace_commission!r}, "
            f"partial_client_commission={self.partial_client_commission!r}, "
            f"client_commission={self.client_commission!r}, "
            f"return_percent={self.return_percent!r}, "
            f"update_date={self.update_date!r}"
            ")"
        )


class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Marketplace.id, ondelete="CASCADE"), nullable=False
    )
    marketplace: Mapped[Marketplace] = relationship(
        "Marketplace", back_populates="warehouses"
    )
    global_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Address.id, ondelete="CASCADE"), nullable=False
    )
    address: Mapped[Address] = relationship(
        Address, uselist=False, back_populates="warehouse"
    )
    leftovers: Mapped[list["Leftover"]] = relationship(
        "Leftover",
        back_populates="warehouse",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    storage_infos: Mapped[list["StorageInfo"]] = relationship(
        "StorageInfo",
        back_populates="warehouse",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    main_coefficient: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint(marketplace_id, global_id),)

    def __repr__(self) -> str:
        return (
            f"Warehouse(id={self.id!r}, "
            f"global_id={self.global_id!r}, "
            f"type={self.type!r}, "
            f"name={self.name!r}, "
            f"main_coefficient={self.main_coefficient!r}"
            ")"
        )


class ProductCard(Base):
    __tablename__ = "product_cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    global_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    seller: Mapped[str] = mapped_column(String(255), nullable=False)
    niche_id: Mapped[int] = mapped_column(
        Integer(), ForeignKey(Niche.id, ondelete="CASCADE"), nullable=False
    )
    niche: Mapped[Niche] = relationship(Niche, back_populates="products")
    histories: Mapped[list["ProductHistory"]] = relationship(
        "ProductHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    storage_info: Mapped["StorageInfo"] = relationship(
        "StorageInfo",
        back_populates="product_card",
        uselist=False,
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint(global_id, niche_id),)

    def __repr__(self) -> str:
        return (
            f"ProductCard(id={self.id!r}, name={self.name!r}, "
            "global_id={self.global_id!r}, "
            "cost={self.cost!r})"
        )


class ProductHistory(Base):
    __tablename__ = "product_histories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost: Mapped[int] = mapped_column(Integer(), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow
    )
    leftovers: Mapped[list["Leftover"]] = relationship(
        "Leftover",
        back_populates="product_history",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ProductCard.id, ondelete="CASCADE"), nullable=False
    )
    product: Mapped[ProductCard] = relationship(ProductCard, back_populates="histories")

    def __repr__(self) -> str:
        return (
            f"ProductCostHistory(id={self.id!r}, "
            "cost={self.cost!r}, "
            "date={self.date!r})"
        )


class Leftover(Base):
    __tablename__ = "leftovers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Warehouse.id, ondelete="CASCADE"), nullable=False
    )
    warehouse: Mapped[Warehouse] = relationship(Warehouse, back_populates="leftovers")
    product_history_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ProductHistory.id, ondelete="CASCADE"), nullable=False
    )
    product_history: Mapped[ProductHistory] = relationship(
        ProductHistory, back_populates="leftovers"
    )

    def __repr__(self) -> str:
        return (
            f"Leftover(id={self.id!r}, type={self.type!r}, quantity={self.quantity!r})"
        )


class StorageInfo(Base):
    __tablename__ = "storage_info"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ProductCard.id, ondelete="CASCADE")
    )
    product_card: Mapped[ProductCard] = relationship(
        ProductCard, back_populates="storage_info"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Warehouse.id, ondelete="CASCADE")
    )
    warehouse: Mapped[Warehouse] = relationship(
        Warehouse, back_populates="storage_infos"
    )
    leftover: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"StorageInfo(id={self.id!r}, leftover={self.leftover!r})"


class EconomyRequest(Base):
    __tablename__ = "economy_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche_id: Mapped[int] = mapped_column(Integer, ForeignKey(Niche.id))
    niche: Mapped[Niche] = relationship(Niche, uselist=False)
    product_exit_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_price: Mapped[int] = mapped_column(Integer, nullable=False)
    lenght: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    mass: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Warehouse.id), nullable=True
    )
    warehouse: Mapped[Warehouse] = relationship(Warehouse, uselist=False)

    def __repr__(self) -> str:
        return (
            f"EconomyRequest(id={self.id!r}, " f"cost_price={self.cost_price!r}, " f")"
        )


class TransitEconomyRequest(Base):
    __tablename__ = "transit_economy_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche_id: Mapped[int] = mapped_column(Integer, ForeignKey(Niche.id))
    niche: Mapped[Niche] = relationship(Niche, uselist=False)
    product_exit_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_price: Mapped[int] = mapped_column(Integer, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    mass: Mapped[int] = mapped_column(Integer, nullable=False)
    logistic_price: Mapped[int] = mapped_column(Integer, nullable=False)
    logistic_count: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_cost_for_cubic_meter: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Warehouse.id), nullable=True
    )
    warehouse: Mapped[Warehouse] = relationship(Warehouse, uselist=False)


class EconomyResult(Base):
    __tablename__ = "economy_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    logistic_price: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    marketplace_expanses: Mapped[int] = mapped_column(Integer, nullable=False)
    absolute_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    relative_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    roi: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_price: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (
            f"EconomyResult(id={self.id!r}, "
            f"result_cost={self.result_cost!r}, "
            f"marketplace_expanses={self.marketplace_expanses!r}, "
            f"logistic_price={self.logistic_price!r}, "
            f"absolute_margin={self.absolute_margin!r}, "
            f"relative_margin={self.relative_margin!r}, "
            f"roi={self.roi!r}, "
        )


class TransitEconomyResult(Base):
    __tablename__ = "transit_economy_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    logistic_price: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    marketplace_expanses: Mapped[int] = mapped_column(Integer, nullable=False)
    absolute_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    relative_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    roi: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_price: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_investments: Mapped[int] = mapped_column(Integer, nullable=False)
    commercial_expanses: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_expanses: Mapped[int] = mapped_column(Integer, nullable=False)
    absolute_transit_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    relative_transit_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    transit_roi: Mapped[int] = mapped_column(Integer, nullable=False)


class UserToEconomy(Base):
    __tablename__ = "users_to_economies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped[User] = relationship(User)
    economy_request_id: Mapped[int] = mapped_column(
        ForeignKey(EconomyRequest.id), nullable=False, unique=True
    )
    economy_request: Mapped[EconomyRequest] = relationship(
        EconomyRequest,
        foreign_keys=[economy_request_id],
    )
    economy_result_id: Mapped[int] = mapped_column(
        ForeignKey(EconomyResult.id), nullable=False, unique=True
    )
    economy_result: Mapped[EconomyResult] = relationship(
        EconomyResult,
        foreign_keys=[economy_result_id],
    )
    recommended_economy_request_id: Mapped[int] = mapped_column(
        ForeignKey(EconomyRequest.id), nullable=False, unique=True
    )
    recommended_economy_request: Mapped[EconomyRequest] = relationship(
        EconomyRequest,
        foreign_keys=[recommended_economy_request_id],
    )
    recommended_economy_result_id: Mapped[int] = mapped_column(
        ForeignKey(EconomyResult.id), nullable=False, unique=True
    )
    recommended_economy_result: Mapped[EconomyResult] = relationship(
        EconomyResult,
        foreign_keys=[recommended_economy_result_id],
    )


class UserToTransitEconomy(Base):
    __tablename__ = "users_to_transit_economies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped[User] = relationship(User)
    transit_request_id: Mapped[int] = mapped_column(
        ForeignKey(TransitEconomyRequest.id),
        nullable=False,
    )
    transit_request: Mapped[TransitEconomyRequest] = relationship(
        TransitEconomyRequest,
        foreign_keys=[transit_request_id],
    )
    transit_result_id: Mapped[int] = mapped_column(
        ForeignKey(TransitEconomyResult.id), nullable=False
    )
    transit_result: Mapped[TransitEconomyResult] = relationship(
        TransitEconomyResult,
        foreign_keys=[transit_result_id],
    )
    recommended_transit_request_id: Mapped[int] = mapped_column(
        ForeignKey(TransitEconomyRequest.id), nullable=False
    )
    recommended_transit_request: Mapped[TransitEconomyRequest] = relationship(
        TransitEconomyRequest,
        foreign_keys=[recommended_transit_request_id],
    )
    recommended_transit_result_id: Mapped[int] = mapped_column(
        ForeignKey(TransitEconomyResult.id), nullable=False
    )
    recommended_transit_result: Mapped[TransitEconomyResult] = relationship(
        TransitEconomyResult,
        foreign_keys=[recommended_transit_result_id],
    )


class NicheCharacteristicsCalculationResult(Base):
    __tablename__ = "niche_characteristics_calculation_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    niche_id: Mapped[int] = mapped_column(
        ForeignKey(Niche.id, ondelete="CASCADE"), nullable=False, unique=True
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow
    )
    niche: Mapped[Niche] = relationship(Niche)
    card_count: Mapped[int] = mapped_column(Integer, nullable=True)
    niche_profit: Mapped[int] = mapped_column(Integer, nullable=True)
    card_trade_count: Mapped[int] = mapped_column(Integer, nullable=True)
    mean_card_rating: Mapped[int] = mapped_column(Integer, nullable=True)
    card_with_trades_count: Mapped[int] = mapped_column(Integer, nullable=True)
    daily_mean_niche_profit: Mapped[int] = mapped_column(Integer, nullable=True)
    daily_mean_trade_count: Mapped[int] = mapped_column(Integer, nullable=True)
    mean_traded_card_cost: Mapped[int] = mapped_column(Integer, nullable=True)
    month_mean_niche_profit_per_card: Mapped[int] = mapped_column(
        Integer, nullable=True
    )
    monopoly_percent: Mapped[int] = mapped_column(Integer, nullable=True)
    maximum_profit_idx: Mapped[int] = mapped_column(Integer, nullable=True)
