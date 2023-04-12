import unittest

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.infrastructure.niche_mappers import \
    NicheTableToJormMapper
from jarvis_db.repositores.market.infrastructure.niche_repository import \
    NicheRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.tables import Category, Marketplace, Niche
from tests.db_context import DbContext


class NicheServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='qwerty')
            category = Category(name='qwerty', marketplace=marketplace)
            session.add(category)
            session.flush()
            self.__category_id = category.id
            self.__marketplace_id = marketplace.id

    def test_create(self):
        niche_entity = NicheEntity('niche', {handler_type: (
                                                                   i + 1) * 0.01 for i, handler_type in
                                             enumerate(HandlerType)}, 0.01)
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create(niche_entity, self.__category_id)
        with self.__db_context.session() as session:
            niche = session.execute(
                select(Niche)
                .where(Niche.name == niche_entity.name)
            ).scalar_one()
            self.assertEqual(niche_entity.name, niche.name)
            self.assertEqual(int(niche_entity.returned_percent * 100),
                             niche.return_percent)
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.CLIENT] * 100), niche.client_commission)
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.PARTIAL_CLIENT] * 100), niche.partial_client_commission)
            self.assertEqual(
                int(niche_entity.commissions[HandlerType.MARKETPLACE] * 100), niche.marketplace_commission)

    def test_create_all(self):
        niche_entities = [NicheEntity(f'niche_{j}', {handler_type: (
                                                                           i + 1) * 0.01 for i, handler_type in
                                                     enumerate(HandlerType)}, 0.01) for j in range(1, 11)]
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create_all(niche_entities, self.__category_id)
        with self.__db_context.session() as session:
            niches = session.execute(
                select(Niche)
                .where(Niche.category_id == self.__category_id)
            ).scalars().all()
            for niche_entity, niche in zip(niche_entities, niches, strict=True):
                self.assertEqual(niche_entity.name, niche.name)
                self.assertEqual(int(niche_entity.returned_percent * 100),
                                 niche.return_percent)
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.CLIENT] * 100), niche.client_commission)
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.PARTIAL_CLIENT] * 100), niche.partial_client_commission)
                self.assertEqual(
                    int(niche_entity.commissions[HandlerType.MARKETPLACE] * 100), niche.marketplace_commission)

    def test_find_by_name(self):
        niche_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            session.add(Niche(
                category_id=self.__category_id,
                name=niche_name,
                marketplace_commission=0.01,
                partial_client_commission=0.02,
                client_commission=0.03,
                return_percent=0.04
            ))
        with self.__db_context.session() as session:
            service = create_service(session)
            niche_entity, _ = service.find_by_name(
                niche_name, self.__category_id)
            self.assertEqual(niche_name, niche_entity.name)

    def test_find_all_in_category(self):
        with self.__db_context.session() as session, session.begin():
            niches = [Niche(
                category_id=self.__category_id,
                name=f'niche_{i}',
                marketplace_commission=0.01,
                partial_client_commission=0.02,
                client_commission=0.03,
                return_percent=0.04
            ) for i in range(1, 11)]
            mapper = NicheTableToJormMapper()
            expected_niches = [mapper.map(niche) for niche in niches]
            session.add_all(niches)
        with self.__db_context.session() as session:
            service = create_service(session)
            niche_entities = service.find_all_in_category(
                self.__category_id).values()
            for niche_entity, niche in zip(niche_entities, expected_niches, strict=True):
                self.assertEqual(niche, niche_entity)

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session, session.begin():
            niches = [Niche(
                category_id=self.__category_id,
                name=f'niche_{i}',
                marketplace_commission=0.01,
                partial_client_commission=0.02,
                client_commission=0.03,
                return_percent=0.04
            ) for i in range(1, 11)]
            mapper = NicheTableToJormMapper()
            expected_niches = [mapper.map(niche) for niche in niches]
            session.add_all(niches)
        with self.__db_context.session() as session:
            service = create_service(session)
            niche_entities = service.find_all_in_marketplace(
                self.__category_id).values()
            for niche_entity, niche in zip(niche_entities, expected_niches, strict=True):
                self.assertEqual(niche, niche_entity)


def create_service(session: Session) -> NicheService:
    return NicheService(NicheRepository(session), NicheTableToJormMapper())