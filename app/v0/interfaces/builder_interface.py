from abc import ABC, abstractmethod
from typing import Self, List, TypeVar

from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import Base

M = TypeVar("M", bound=Base)

def IQueryBuilder(ABC):

    @abstractmethod
    def limit(self, value_limit: int) -> Self:
        ...

    @abstractmethod
    def order_by(self, columns: List[ColumnElement]) -> Self:
        ...

    @abstractmethod
    def add_condition(self, column: ColumnElement, value: any) -> Self:
        ...

    @abstractmethod
    async def execute(self, db_session: AsyncSession) -> List[M]:
        ...