import unittest

from jorm.market.items import Product
from sqlalchemy import select

from jarvis_db.factories.mappers import create_product_table_mapper
from jarvis_db.factories.services import create_product_card_service
from jarvis_db.schemas import Niche, ProductCard, ProductToNiche
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder
from tests.helpers import sort_product


class ProductCardServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            seeder.seed_niches(3)

    def test_create(self):
        expected = Product("qwerty", 100, 200, 5.0, "brand", "seller", [])
        mapper = create_product_table_mapper()
        with self.__db_context.session() as session, session.begin():
            service = create_product_card_service(session)
            niche_ids = session.execute(select(Niche.id)).scalars().all()
            product_id = service.create_product(expected, niche_ids)
        with self.__db_context.session() as session:
            found = session.execute(
                select(ProductCard).where(ProductCard.id == product_id)
            ).scalar_one()
            mapper = create_product_table_mapper()
            actual = mapper.map(found)
            expected.category_niche_list = [
                (niche.category.name, niche.name)
                for niche in session.execute(
                    select(ProductCard).where(ProductCard.id == product_id)
                )
                .scalar_one()
                .niches
            ]
            self.assertEqual(expected, actual)

    def test_create_many(self):
        expected_products = [
            Product(
                f"product_{i}",
                100 + 10 * i,
                200 + 20 * i,
                5.0 + i,
                f"brand_{i}",
                f"seller_{i}",
                [],
            )
            for i in range(10)
        ]
        with self.__db_context.session() as session, session.begin():
            service = create_product_card_service(session)
            niche_ids = session.execute(select(Niche.id)).scalars().all()
            service.create_products(expected_products, niche_ids)
        with self.__db_context.session() as session:
            found = session.execute(select(ProductCard)).scalars().all()
            mapper = create_product_table_mapper()
            actual_products = [mapper.map(product) for product in found]
            for expected, actual in zip(
                expected_products, actual_products, strict=True
            ):
                expected.category_niche_list = [
                    (niche.category.name, niche.name)
                    for niche in session.execute(
                        select(ProductCard).where(
                            ProductCard.global_id == expected.global_id
                        )
                    )
                    .scalar_one()
                    .niches
                ]
                self.assertEqual(expected, actual)

    def test_find_by_id(self):
        product_id = 100
        mapper = create_product_table_mapper()
        with self.__db_context.session() as session, session.begin():
            product = ProductCard(
                id=product_id,
                name="product_name",
                global_id=200,
                cost=1000,
                rating=5.0,
                brand="brand_name",
                seller="seller_name",
            )
            session.add(product)
            session.flush()
            expected = mapper.map(product)
            self.assertEqual(0, len(expected.history.get_history()))
            seeder = AlchemySeeder(session)
            seeder.seed_product_histories(200)
        with self.__db_context.session() as session:
            service = create_product_card_service(session)
            actual = service.find_by_id(product_id)
            expected.category_niche_list = [
                (niche.category.name, niche.name)
                for niche in session.execute(
                    select(ProductCard).where(ProductCard.id == product_id)
                )
                .scalar_one()
                .niches
            ]
            assert actual is not None
            self.assertEqual(expected, actual)

    def test_find_by_it_atomic(self):
        product_id = 100
        mapper = create_product_table_mapper()
        with self.__db_context.session() as session, session.begin():
            product = ProductCard(
                id=product_id,
                name="product_name",
                global_id=200,
                cost=1000,
                rating=5.0,
                brand="brand_name",
                seller="seller_name",
            )
            session.add(product)
            session.flush()
            seeder = AlchemySeeder(session)
            seeder.seed_warehouses(20)
            actual_histories_count = 50
            seeder.seed_product_histories(actual_histories_count)
            actual_leftovers_count = 5000
            seeder.seed_leftovers(actual_leftovers_count)
            expected = mapper.map(product)
            self.assertEqual(
                actual_histories_count, len(expected.history.get_history())
            )
            self.assertEqual(
                actual_leftovers_count,
                sum(
                    [
                        len(leftovers)
                        for unit in expected.history.get_history()
                        for leftovers in unit.leftover.values()
                    ]
                ),
            )
            sort_product(expected)
        with self.__db_context.session() as session:
            service = create_product_card_service(session)
            actual = service.find_by_id_atomic(product_id)
            assert actual is not None
            sort_product(actual)
            self.assertEqual(expected, actual)

    def test_find_by_global_id(self):
        mapper = create_product_table_mapper()
        global_id = 200
        product_id = 100
        with self.__db_context.session() as session, session.begin():
            product = ProductCard(
                id=product_id,
                name="product_name",
                global_id=global_id,
                cost=1000,
                rating=5.0,
                brand="brand_name",
                seller="seller_name",
            )
            niche_ids = list(session.execute(select(Niche.id)).scalars().all())
            session.add(product)
            session.flush()
            session.add_all(
                (
                    ProductToNiche(product_id=product.id, niche_id=niche_id)
                    for niche_id in niche_ids
                )
            )
            session.flush()
            expected = mapper.map(product)
            self.assertEqual(0, len(expected.history.get_history()))
            seeder = AlchemySeeder(session)
            seeder.seed_product_histories(200)
        with self.__db_context.session() as session:
            service = create_product_card_service(session)
            actual = service.find_by_global_id(global_id, niche_ids[0])
            assert actual is not None
            self.assertTupleEqual((expected, product_id), actual)

    def test_find_all_in_niche(self):
        mapper = create_product_table_mapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(2)
            seeder.seed_products(100)
            products = session.execute(select(ProductCard)).scalars().all()
            niche_id = session.execute(
                select(Niche.id).order_by(Niche.id).limit(1)
            ).scalar_one()
            expected_products = {
                product.id: mapper.map(product)
                for product in products
                if niche_id in (niche.id for niche in product.niches)
            }
            self.assertTrue(
                all(
                    (
                        len(product.history.get_history()) == 0
                        for product in expected_products.values()
                    )
                )
            )
        with self.__db_context.session() as session:
            service = create_product_card_service(session)
            actual_products = service.find_all_in_niche(niche_id)
            self.assertDictEqual(expected_products, actual_products)

    def test_filter_existing_ids(self):
        existing_ids = [i for i in range(100, 111)]
        with self.__db_context.session() as session, session.begin():
            niche_id = session.execute(
                select(Niche.id).order_by(Niche.id).limit(1)
            ).scalar_one()
            products = [
                ProductCard(
                    id=index,
                    name=f"product_{global_id}",
                    global_id=global_id,
                    cost=100 * global_id,
                    rating=5.0 + global_id,
                    brand=f"brand_{index}",
                    seller=f"seller_{index}",
                )
                for index, global_id in enumerate(existing_ids, start=1)
            ]
            session.add_all(products)
            session.flush()
            session.add_all(
                (
                    ProductToNiche(product_id=product.id, niche_id=niche_id)
                    for product in products
                )
            )
        new_ids = [i for i in range(200, 211)]
        with self.__db_context.session() as session:
            service = create_product_card_service(session)
            filtered_ids = service.filter_existing_global_ids(
                niche_id, [*existing_ids, *new_ids]
            )
            self.assertEqual(sorted(new_ids), sorted(filtered_ids))

    def test_update(self):
        product_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(
                ProductCard(
                    id=product_id,
                    name="product_100",
                    global_id=20,
                    cost=10,
                    rating=5.0,
                    brand="brand",
                    seller="seller",
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_product_card_service(session)
            expected = Product("product_1", 100, 25, 8.0, "new_brand", "new_seller", [])
            service.update(product_id, expected)
            product = session.execute(
                select(ProductCard).where(ProductCard.id == product_id)
            ).scalar_one()
            mapper = create_product_table_mapper()
            actual = mapper.map(product)
            self.assertEqual(expected, actual)

    def test_add_niche_to_product(self):
        with self.__db_context.session() as session, session.begin():
            product_id = 1
            session.add(
                ProductCard(
                    id=product_id,
                    name="product_100",
                    global_id=20,
                    cost=10,
                    rating=5.0,
                    brand="brand",
                    seller="seller",
                )
            )
            niche_id = session.execute(select(Niche.id).limit(1)).scalar_one()
        with self.__db_context.session() as session, session.begin():
            service = create_product_card_service(session)
            service.add_niche_to_product(product_id, niche_id)
        with self.__db_context.session() as session:
            product = session.execute(
                select(ProductCard).where(ProductCard.id == product_id)
            ).scalar_one()
            self.assertIn(niche_id, (niche.id for niche in product.niches))

    def test_remove_niche_from_product(self):
        with self.__db_context.session() as session, session.begin():
            product_id = 1
            session.add(
                ProductCard(
                    id=product_id,
                    name="product_100",
                    global_id=20,
                    cost=10,
                    rating=5.0,
                    brand="brand",
                    seller="seller",
                )
            )
            niche_id = session.execute(select(Niche.id).limit(1)).scalar_one()
            session.add(ProductToNiche(product_id=product_id, niche_id=niche_id))
        with self.__db_context.session() as session, session.begin():
            service = create_product_card_service(session)
            service.remove_niche_from_product(product_id, niche_id)
        with self.__db_context.session() as session:
            product = session.execute(
                select(ProductCard).where(ProductCard.id == product_id)
            ).scalar_one()
            self.assertNotIn(niche_id, (niche.id for niche in product.niches))
