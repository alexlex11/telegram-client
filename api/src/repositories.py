from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.orm import DeclarativeBase, Session

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType], ABC):
    @property
    @abstractmethod
    def model(self) -> Type[ModelType]:
        raise NotImplementedError

    def add(self, session: Session, **data) -> ModelType:
        query = insert(self.model).values(**data).returning(self.model)
        result = session.execute(query)
        return result.scalar_one_or_none()

    def get(self, session: Session, **filter_by) -> ModelType | None:
        query = select(self.model).filter_by(**filter_by)
        result = session.execute(query)
        return result.scalar_one_or_none()

    def update(self, session: Session, filter_by: dict, **data) -> ModelType | None:
        query = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data)
            .returning(self.model)
        )
        result = session.execute(query)
        return result.scalar_one_or_none()

    def rem(self, session: Session, **filter_by) -> None:
        query = delete(self.model).filter_by(**filter_by)
        session.execute(query)

    def get_all(self, session: Session, **filter_by) -> list[ModelType]:
        query = select(self.model).filter_by(**filter_by)
        result = session.execute(query)
        return result.scalars().all()

    def len(self, session: Session, **filter_by) -> int:
        query = select(func.count()).select_from(self.model).filter_by(**filter_by)
        result = session.execute(query)
        return result.scalar_one()
