from data_providers.wildberries_data_provider import WildBerriesDataProvider
from sqlalchemy.orm import sessionmaker
from tables import Category, Niche, Product, ProductCostHistory


class DbFiller:

    def __init__(self, api: WildBerriesDataProvider, sessionmaker: sessionmaker):
        self.__api = api
        self.__sessionmaker = sessionmaker

    def fill_categories(self):
        categories = self.__api.get_categories()
        with self.__sessionmaker() as session:
            with session.begin():
                db_categories = []
                for category in categories:
                    db_categories.append(Category(name=category))
                session.add_all(db_categories)

    def fill_niches(self):
        with self.__sessionmaker() as session:
            with session.begin():
                category_to_id = {
                    c.name: c.id for c in session.query(Category).all()
                }
                category_to_niches = self.__api.get_niches(
                    category_to_id.keys()
                )
                db_niches = []
                for category, niches in category_to_niches.items():
                    category_id = category_to_id[category]
                    for niche in niches:
                        db_niches.append(
                            Niche(name=niche,
                                  category_id=category_id)
                        )
                session.add_all(db_niches)

    def fill_niche_products(self, niche: str, pages: int = 1):
        with self.__sessionmaker() as session:
            with session.begin():
                db_products = []
                niche_id = session.query(Niche).filter(
                    Niche.name == niche).first().id
                products = self.__api.get_products_by_niche(niche, pages)
                for product in products:
                    db_products.append(Product(
                        id=product[1],
                        name=product[0],
                        niche_id=niche_id
                    ))
                session.add_all(db_products)

    def fill_niche_price_history(self, niche: str):
        with self.__sessionmaker() as session:
            with session.begin():
                db_histories = []
                niche_id = session.query(Niche).filter(
                    Niche.name == niche).first().id
                products: list[Product] = session.query(
                    Product).filter(Product.niche_id == niche_id).all()
                for product in products:
                    histories = self.__api.get_product_price_history(
                        product.id)
                    for history in histories:
                        db_histories.append(
                            ProductCostHistory(
                                cost=history[0],
                                date=history[1],
                                product_id=product.id
                            ))
                session.add_all(db_histories)
