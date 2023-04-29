from typing import Generic, Iterable, TypeVar

from sqlalchemy.orm import Session

T = TypeVar('T')


class AlchemyRepository(Generic[T]):
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: T):
        self._session.add(entity)
        self._session.flush()

    def add_all(self, entities: Iterable[T]):
        self._session.add_all(entities)
        self._session.flush()

    def save(self, entity: T) -> T:
        self._session.add(entity)
        self._session.flush()
        return entity

    def update(self, entity: T) -> T:
        self._session.merge(entity)
        self._session.flush()
        return entity

    def delete(self, entity: T):
        self._session.delete(entity)
        self._session.flush()
