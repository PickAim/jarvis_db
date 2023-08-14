import unittest
from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select
from sqlalchemy.orm import contains_eager

from jarvis_db import schemas
from jarvis_db.factories.mappers import create_niche_table_mapper
from jarvis_db.factories.services import create_niche_service
from jarvis_db.schemas import Leftover, Niche, ProductCard, ProductHistory
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class NicheServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(1)
            session.flush()
            category = session.execute(select(schemas.Category)).scalar_one()
            self.__category_id = category.id
            self.__marketplace_id = category.marketplace_id

    def test_create(self):
        niche_entity = NicheEntity(
            "niche",
            {
                handler_type: (i + 1) * 0.01
                for i, handler_type in enumerate(HandlerType)
            },
            0.01,
        )
        with self.__db_context.session() as session, session.begin():
            service = create_niche_service(session)
            service.create(niche_entity, self.__category_id)
        with self.__db_context.session() as session:
            niche = session.execute(
                select(Niche).where(Niche.name == niche_entity.name)
            ).scalar_one()
            self.assertEqual(niche_entity.name, niche.name)
            self.assertEqual(
                int(niche_entity.returned_percent * 100), niche.return_percent
            )
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.CLIENT] * 100),
                niche.client_commission,
            )
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.PARTIAL_CLIENT] * 100),
                niche.partial_client_commission,
            )
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.MARKETPLACE] * 100),
                niche.marketplace_commission,
            )

    def test_create_all(self):
        niche_entities = [
            NicheEntity(
                f"niche_{j}",
                {
                    handler_type: (i + 1) * 0.01
                    for i, handler_type in enumerate(HandlerType)
                },
                0.01,
            )
            for j in range(1, 11)
        ]
        with self.__db_context.session() as session, session.begin():
            service = create_niche_service(session)
            service.create_all(niche_entities, self.__category_id)
        with self.__db_context.session() as session:
            niches = (
                session.execute(
                    select(Niche).where(Niche.category_id == self.__category_id)
                )
                .scalars()
                .all()
            )
            for niche_entity, niche in zip(niche_entities, niches, strict=True):
                self.assertEqual(niche_entity.name, niche.name)
                self.assertEqual(
                    int(niche_entity.returned_percent * 100), niche.return_percent
                )
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.CLIENT] * 100),
                    niche.client_commission,
                )
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.PARTIAL_CLIENT] * 100),
                    niche.partial_client_commission,
                )
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.MARKETPLACE] * 100),
                    niche.marketplace_commission,
                )

    def test_find_by_name(self):
        niche_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Niche(
                    category_id=self.__category_id,
                    name=niche_name,
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
            )
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            result = service.find_by_name(niche_name, self.__category_id)
            assert result is not None
            niche_entity, _ = result
            self.assertEqual(niche_name, niche_entity.name)

    def test_find_by_id(self):
        mapper = create_niche_table_mapper()
        niche_id = 100
        with self.__db_context.session() as session, session.begin():
            niche = Niche(
                id=niche_id,
                category_id=self.__category_id,
                name="niche_name",
                marketplace_commission=0.01,
                partial_client_commission=0.02,
                client_commission=0.03,
                return_percent=0.04,
            )
            session.add(niche)
            session.flush()
            expected = mapper.map(niche)
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual = service.find_by_id(niche_id)
            self.assertEqual(expected, actual)

    def test_fetch_by_id_atomic(self):
        niche_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(
                Niche(
                    id=niche_id,
                    category_id=self.__category_id,
                    name="niche_name",
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
            )
            session.flush()
            seeder = AlchemySeeder(session)
            seeder.seed_products(5)
            seeder.seed_product_histories(10)
            seeder.seed_leftovers(50)
            mapper = create_niche_table_mapper()
            expected_niche = mapper.map(
                session.execute(
                    select(Niche)
                    .join(Niche.category)
                    .outerjoin(Niche.products)
                    .outerjoin(ProductCard.histories)
                    .outerjoin(ProductHistory.leftovers)
                    .join(Leftover.warehouse)
                    .where(Niche.id == niche_id)
                    .order_by(Leftover.type, Leftover.quantity)
                    .options(
                        contains_eager(Niche.category),
                        contains_eager(Niche.products)
                        .contains_eager(ProductCard.histories)
                        .contains_eager(ProductHistory.leftovers)
                        .contains_eager(Leftover.warehouse),
                    )
                )
                .unique()
                .scalar_one()
            )
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual_niche = service.fetch_by_id_atomic(niche_id)
            assert actual_niche is not None
            self.assertEqual(expected_niche, actual_niche)

    def test_find_all_in_category(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(2)
            seeder.seed_niches(30)
            niches = session.execute(select(schemas.Niche)).scalars().all()
            mapper = create_niche_table_mapper()
            expected_niches = [
                mapper.map(niche)
                for niche in niches
                if niche.category_id == self.__category_id
            ]
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual_niches = service.find_all_in_category(self.__category_id).values()
            for expected, actual in zip(expected_niches, actual_niches, strict=True):
                self.assertEqual(expected, actual)

    def test_fetch_all_in_category_atomic(self):
        def sort_niches(niche_iterable: Iterable[NicheEntity]):
            for niche in niche_iterable:
                niche.products.sort(key=lambda x: x.name)
                for product in niche.products:
                    for history in product.history:
                        for leftovers in history.leftover.values():
                            leftovers.sort(key=lambda unit: unit.specify)
                            leftovers.sort(key=lambda unit: unit.leftover)

        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(2)
            seeder.seed_niches(4)
            seeder.seed_products(12)
            seeder.seed_product_histories(80)
            seeder.seed_leftovers(160)
            niches = (
                session.execute(
                    select(schemas.Niche)
                    .outerjoin(schemas.Niche.products)
                    .outerjoin(schemas.ProductCard.histories)
                    .outerjoin(schemas.ProductHistory.leftovers)
                    .outerjoin(schemas.Leftover.warehouse)
                    .where(Niche.category_id == self.__category_id)
                    .distinct()
                )
                .unique()
                .scalars()
                .all()
            )
            mapper = create_niche_table_mapper()
            expected_niches = {
                niche.id: mapper.map(niche)
                for niche in niches
                if niche.category_id == self.__category_id
            }
            sort_niches(expected_niches.values())
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual_niches = service.fetch_all_in_category_atomic(self.__category_id)
            sort_niches(actual_niches.values())
            self.assertEqual(len(expected_niches), len(actual_niches))
            self.assertDictEqual(expected_niches, actual_niches)

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(30)
            niches = session.execute(select(schemas.Niche)).scalars().all()
            mapper = create_niche_table_mapper()
            expected_niches = [
                mapper.map(niche)
                for niche in niches
                if niche.category.marketplace_id == self.__marketplace_id
            ]
            session.add_all(niches)
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            niche_entities = service.find_all_in_marketplace(
                self.__marketplace_id
            ).values()
            for niche_entity, niche in zip(
                niche_entities, expected_niches, strict=True
            ):
                self.assertEqual(niche, niche_entity)

    def test_exists_with_name_returns_true(self):
        niche_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Niche(
                    category_id=self.__category_id,
                    name=niche_name,
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
            )
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            exists = service.exists_with_name(niche_name, self.__category_id)
            self.assertTrue(exists)

    def test_exists_with_name_returns_false(self):
        niche_name = "qwerty"
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            exists = service.exists_with_name(niche_name, self.__category_id)
            self.assertFalse(exists)

    def test_filter_existing_names(self):
        existing_names = [f"niche_{i}" for i in range(1, 11)]
        with self.__db_context.session() as session, session.begin():
            session.add_all(
                (
                    Niche(
                        category_id=self.__category_id,
                        name=niche_name,
                        marketplace_commission=0.01,
                        partial_client_commission=0.02,
                        client_commission=0.03,
                        return_percent=0.04,
                    )
                    for niche_name in existing_names
                )
            )
        new_names = [f"new_niche_name_{i}" for i in range(1, 11)]
        names_to_filter = [*existing_names, *new_names]
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            filtered_names = service.filter_existing_names(
                names_to_filter, self.__category_id
            )
            self.assertEqual(sorted(new_names), sorted(filtered_names))

    def test_update(self):
        niche_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(
                Niche(
                    id=niche_id,
                    category_id=self.__category_id,
                    name="niche_name",
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
            )
        updated_name = "updated_name"
        marketplace_commission = 0.015
        partial_client_commission = 0.025
        client_commission = 0.035
        return_percent = 0.045
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            service.update(
                niche_id,
                NicheEntity(
                    updated_name,
                    {
                        HandlerType.MARKETPLACE: marketplace_commission,
                        HandlerType.PARTIAL_CLIENT: partial_client_commission,
                        HandlerType.CLIENT: client_commission,
                    },
                    return_percent,
                ),
            )
            session.flush()
            actual = session.execute(
                select(Niche).where(Niche.id == niche_id)
            ).scalar_one()
            self.assertEqual(updated_name, actual.name)
            self.assertEqual(
                int(marketplace_commission * 100), actual.marketplace_commission
            )
            self.assertEqual(
                int(partial_client_commission * 100), actual.partial_client_commission
            )
            self.assertEqual(int(client_commission * 100), actual.client_commission)
            self.assertEqual(int(return_percent * 100), actual.return_percent)


if __name__ == "__main__":
    unittest.main()
