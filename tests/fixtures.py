from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.tables import (
    Account,
    Address,
    Category,
    Leftover,
    Marketplace,
    Niche,
    Pay,
    ProductCard,
    ProductHistory,
    TokenSet,
    User,
    Warehouse,
)


class AlchemySeeder:
    def __init__(self, session: Session):
        self.__session = session

    def seed_accounts(self):
        self.__session.add_all(create_accounts(25))
        self.__session.flush()

    def seed_users(self):
        accounts = list(self.__session.execute(select(Account)).scalars().all())
        users = create_users(accounts)
        self.__session.add_all(users)
        self.__session.flush()

    def seed_marketplaces(self, quantity: int):
        self.__session.add_all(create_marketplaces(quantity))
        self.__session.flush()

    def seed_addresses(self, quantity: int):
        self.__session.add_all(create_addresses(quantity))
        self.__session.flush()

    def seed_warehouses(self, quantity: int):
        def retrieve_addresses():
            return list(self.__session.execute(select(Address)).scalars().all())

        def retrieve_marketplaces():
            return list(self.__session.execute(select(Marketplace)).scalars().all())

        addresses = retrieve_addresses()
        if not addresses:
            self.seed_addresses(quantity)
            addresses = retrieve_addresses()
        marketplaces = retrieve_marketplaces()
        if not marketplaces:
            self.seed_marketplaces(3)
            marketplaces = retrieve_marketplaces()
        warehouses = create_warehouses(quantity, marketplaces, addresses)
        self.__session.add_all(warehouses)
        self.__session.flush()

    def seed_categories(self, quantity: int):
        def retrieve_marketplaces():
            return list(self.__session.execute(select(Marketplace)).scalars().all())

        marketplaces = retrieve_marketplaces()
        if not marketplaces:
            self.seed_marketplaces(3)
            marketplaces = retrieve_marketplaces()
        categories = create_categories(quantity, marketplaces)
        for category in categories:
            if (
                self.__session.execute(
                    select(Category)
                    .where(Category.marketplace_id == category.marketplace.id)
                    .where(Category.name == category.name)
                ).scalar_one_or_none()
                is not None
            ):
                category.name += "#"
        self.__session.add_all(categories)
        self.__session.flush()

    def seed_niches(self, quantity: int):
        def retrieve_categories():
            return list(self.__session.execute(select(Category)).scalars().all())

        categories = retrieve_categories()
        if not categories:
            self.seed_categories(5)
            categories = retrieve_categories()
        niches = create_niches(quantity, categories)
        for niche in niches:
            if (
                self.__session.execute(
                    select(Niche)
                    .where(Niche.category_id == niche.category.id)
                    .where(Niche.name == niche.name)
                ).scalar_one_or_none()
                is not None
            ):
                niche.name += "#"
        self.__session.add_all(niches)
        self.__session.flush()

    def seed_products(self, quantity: int):
        def retrieve_niches():
            return list(self.__session.execute(select(Niche)).scalars().all())

        niches = retrieve_niches()
        if not niches:
            self.seed_niches(15)
            niches = retrieve_niches()
        products = create_products(quantity, niches)
        self.__session.add_all(products)
        self.__session.flush()

    def seed_product_histories(self, quantity: int):
        def retrieve_products():
            return list(self.__session.execute(select(ProductCard)).scalars().all())

        products = retrieve_products()
        if not products:
            self.seed_products(10)
            products = retrieve_products()
        histories = create_product_histories(quantity, products)
        self.__session.add_all(histories)
        self.__session.flush()

    def seed_leftovers(self, quantity: int):
        def retrieve_histories():
            return list(self.__session.execute(select(ProductHistory)).scalars().all())

        def retrieve_warehouses():
            return list(self.__session.execute(select(Warehouse)).scalars().all())

        histories = retrieve_histories()
        if not histories:
            self.seed_product_histories(50)
            histories = retrieve_histories()
        warehouses = retrieve_warehouses()
        if not warehouses:
            self.seed_warehouses(5)
            warehouses = retrieve_warehouses()
        leftovers = create_leftovers(quantity, histories, warehouses)
        self.__session.add_all(leftovers)
        self.__session.flush()


def create_accounts(quantity: int) -> list[Account]:
    return [
        Account(
            phone=f"phone_{i}",
            email=f"email{i}@mail.org",
            password=f"password_{i}",
        )
        for i in range(quantity)
    ]


def create_users(accounts: list[Account]) -> list[User]:
    return [
        User(name=f"username{i}", account=account) for i, account in enumerate(accounts)
    ]


def create_token_sets(users: list[User]) -> list[TokenSet]:
    return [
        TokenSet(
            access_token=f"access_token_{i}",
            refresh_token=f"refresh_token_{i}",
            fingerprint_token=f"fingerprint_token_{i}",
            user=user,
        )
        for i, user in enumerate(users)
    ]


def create_pays(self) -> list[Pay]:
    return []


def create_addresses(quantity: int) -> list[Address]:
    return [
        Address(
            country=f"country_{i}",
            region=f"region_{i}",
            street=f"street_{i}",
            number=f"number_{i}",
            corpus=f"corpus_{i}",
        )
        for i in range(quantity)
    ]


def create_marketplaces(quantity: int) -> list[Marketplace]:
    return [Marketplace(name=f"marketplace_{i}") for i in range(quantity)]


def create_categories(quantity: int, marketplaces: list[Marketplace]) -> list[Category]:
    return [
        Category(
            name=f"category_{i}",
            marketplace=marketplaces[i % len(marketplaces)],
        )
        for i in range(quantity)
    ]


def create_niches(quantity: int, categories: list[Category]) -> list[Niche]:
    return [
        Niche(
            name=f"niche_{i}",
            category=categories[i % len(categories)],
            marketplace_commission=i % 25,
            partial_client_commission=i & 15,
            client_commission=i % 10,
            return_percent=i % 20,
        )
        for i in range(quantity)
    ]


def create_products(quantity: int, niches: list[Niche]) -> list[ProductCard]:
    return [
        ProductCard(
            name=f"product_{i}",
            global_id=i + 200,
            cost=i * 100,
            rating=i % 100,
            brand=f"brand_{i}",
            seller=f"seller_{i}",
            niche=niches[i % len(niches)],
        )
        for i in range(quantity)
    ]


def create_warehouses(
    quantity: int, marketplaces: list[Marketplace], addresses: list[Address]
) -> list[Warehouse]:
    return [
        Warehouse(
            owner=marketplaces[i % len(marketplaces)],
            global_id=200 + i,
            type=1,
            name=f"warehouse_name_{i}",
            address=addresses[i % len(addresses)],
            basic_logistic_to_customer_commission=0,
            additional_logistic_to_customer_commission=0,
            logistic_from_customer_commission=0,
            basic_storage_commission=0,
            additional_storage_commission=0,
            monopalette_storage_commission=0,
        )
        for i in range(quantity)
    ]


def create_product_histories(
    quantity: int,
    products: list[ProductCard],
) -> list[ProductHistory]:
    return [
        ProductHistory(cost=100 + 200 * i, product=products[i % len(products)])
        for i in range(quantity)
    ]


def create_leftovers(
    quantity: int, histories: list[ProductHistory], warehouses: list[Warehouse]
) -> list[Leftover]:
    return [
        Leftover(
            type=f"leftover_type_{i}",
            quantity=10 * i,
            warehouse=warehouses[i % len(warehouses)],
            product_history=histories[i % len(histories)],
        )
        for i in range(quantity)
    ]
