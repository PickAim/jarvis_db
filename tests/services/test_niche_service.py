import unittest

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select

from jarvis_db import tables
from jarvis_db.factories.services import create_niche_service
from jarvis_db.repositores.mappers.market.infrastructure.niche_mappers import (
    NicheTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.items.product_mappers import (
    ProductTableToJormMapper,
)
from jarvis_db.tables import Niche
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class NicheServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(1)
            session.flush()
            category = session.execute(select(tables.Category)).scalar_one()
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
            seeder.seed_products(10)
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
            expected_niche = mapper.map(
                session.execute(
                    select(Niche)
                    .outerjoin(Niche.products)
                    .where(Niche.id == niche_id)
                    .distinct()
                ).scalar_one()
            )
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual_niche = service.fetch_by_id_atomic(niche_id)
            self.assertEqual(expected_niche.name, actual_niche.name)
            self.assertEqual(expected_niche.commissions, actual_niche.commissions)
            self.assertEqual(
                expected_niche.returned_percent, actual_niche.returned_percent
            )
            self.assertEqual(len(expected_niche.products), len(actual_niche.products))

    def test_find_all_in_category(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(2)
            seeder.seed_niches(30)
            niches = session.execute(select(tables.Niche)).scalars().all()
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
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
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_categories(2)
            seeder.seed_niches(30)
            seeder.seed_products(300)
            niches = (
                session.execute(
                    select(tables.Niche).outerjoin(tables.Niche.products).distinct()
                )
                .scalars()
                .all()
            )
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
            expected_niches = [
                mapper.map(niche)
                for niche in niches
                if niche.category_id == self.__category_id
            ]
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            actual_niches = service.fetch_all_in_category_atomic(
                self.__category_id
            ).values()
            for expected, actual in zip(expected_niches, actual_niches, strict=True):
                self.assertEqual(expected.name, actual.name)
                self.assertEqual(expected.commissions, actual.commissions)
                self.assertEqual(expected.returned_percent, actual.returned_percent)
                self.assertEqual(len(expected.products), len(actual.products))

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(30)
            niches = session.execute(select(tables.Niche)).scalars().all()
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
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
