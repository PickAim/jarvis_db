import unittest

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select

from jarvis_db.repositores.mappers.market.infrastructure.niche_mappers import (
    NicheTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.items.product_mappers import (
    ProductTableToJormMapper,
)
from jarvis_db.repositores.market.infrastructure.niche_repository import NicheRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.tables import Category, Marketplace, Niche
from tests.db_context import DbContext
from jarvis_db.factories.services import create_niche_service


class NicheServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name="qwerty")
            category = Category(name="qwerty", marketplace=marketplace)
            session.add(category)
            session.flush()
            self.__category_id = category.id
            self.__marketplace_id = marketplace.id

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

    def test_find_all_in_category(self):
        with self.__db_context.session() as session, session.begin():
            niches = [
                Niche(
                    category_id=self.__category_id,
                    name=f"niche_{i}",
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
                for i in range(1, 11)
            ]
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
            expected_niches = [mapper.map(niche) for niche in niches]
            session.add_all(niches)
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            niche_entities = service.find_all_in_category(self.__category_id).values()
            for niche_entity, niche in zip(
                niche_entities, expected_niches, strict=True
            ):
                self.assertEqual(niche, niche_entity)

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session, session.begin():
            niches = [
                Niche(
                    category_id=self.__category_id,
                    name=f"niche_{i}",
                    marketplace_commission=0.01,
                    partial_client_commission=0.02,
                    client_commission=0.03,
                    return_percent=0.04,
                )
                for i in range(1, 11)
            ]
            mapper = NicheTableToJormMapper(ProductTableToJormMapper())
            expected_niches = [mapper.map(niche) for niche in niches]
            session.add_all(niches)
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            niche_entities = service.find_all_in_marketplace(
                self.__category_id
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

    def test_exists_with_name_returs_false(self):
        niche_name = "qwerty"
        with self.__db_context.session() as session:
            service = create_niche_service(session)
            exists = service.exists_with_name(niche_name, self.__category_id)
            self.assertFalse(exists)

    def test_filther_existing_names(self):
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
