from sqlalchemy import select
from jarvis_db.tables import (
    Account,
    Address,
    Category,
    Marketplace,
    Niche,
    Pay,
    ProductCard,
    TokenSet,
    User,
    Warehouse,
)
from sqlalchemy.orm import Session


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


def create_warehouses(self) -> list[Warehouse]:
    return [Warehouse() for i, address in enumerate(self.create_addresses())]
