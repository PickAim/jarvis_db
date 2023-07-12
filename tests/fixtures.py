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


class TestFixtures:
    def create_accounts(self) -> list[Account]:
        return [
            Account(
                id=i,
                phone=f"phone_{i}",
                email=f"email{i}@mail.org",
                password=f"password_{i}",
            )
            for i in range(25)
        ]

    def create_users(self) -> list[User]:
        return [
            User(id=i, name=f"username{i}", account=account)
            for i, account in enumerate(self.create_accounts())
        ]

    def create_token_sets(self) -> list[TokenSet]:
        return [
            TokenSet(
                id=1,
                access_token=f"access_token_{i}",
                refresh_token=f"refresh_token_{i}",
                fingerprint_token=f"fingerprint_token_{i}",
                user=user,
            )
            for i, user in enumerate(self.create_users())
        ]

    def create_pays(self) -> list[Pay]:
        return []

    def create_addresses(self) -> list[Address]:
        return [
            Address(
                id=i,
                country=f"country_{i}",
                region=f"region_{i}",
                street=f"street_{i}",
                number=f"number_{i}",
                corpus=f"corpus_{i}",
            )
            for i in range(20)
        ]

    def create_marketplaces(self) -> list[Marketplace]:
        return [Marketplace(id=i, name=f"marketplace_{i}") for i in range(3)]

    def create_categories(self) -> list[Category]:
        marketplaces = self.create_marketplaces()
        return [
            Category(
                id=i,
                name=f"category_{i}",
                marketplace=marketplaces[i % len(marketplaces)],
            )
            for i in range(15)
        ]

    def create_niches(self) -> list[Niche]:
        categories = self.create_categories()
        return [
            Niche(
                id=i,
                name=f"niche_{i}",
                category=categories[i % len(categories)],
                marketplace_commission=i % 25,
                partial_client_commission=i & 15,
                client_commission=i % 10,
                return_percent=i % 20,
            )
            for i in range(25)
        ]

    def create_products(self) -> list[ProductCard]:
        niches = self.create_niches()
        return [
            ProductCard(
                id=i,
                name=f"product_{i}",
                global_id=i + 200,
                cost=i * 100,
                rating=i % 100,
                brand=f"brand_{i}",
                seller=f"seller_{i}",
                niche=niches[i % len(niches)],
            )
            for i in range(100)
        ]

    def create_warehouses(self) -> list[Warehouse]:
        return [Warehouse() for i, address in enumerate(self.create_addresses())]
