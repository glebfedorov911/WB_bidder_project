from abc import ABC, abstractmethod
from typing import Self, List, TypeVar

from pydantic import BaseModel
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import Base


schema_type = TypeVar("S", bound=BaseModel) 
model_type = TypeVar("M", bound=Base)

class IQueryBuilder(ABC):

    @abstractmethod
    def limit(self, value_limit: int) -> Self:
        ...

    @abstractmethod
    def order_by(self, columns: List[ColumnElement]) -> Self:
        ...

    @abstractmethod
    def add_condition(self, column: ColumnElement, value: any, type_operation: str = "e") -> Self:
        ...

    @abstractmethod
    async def execute(self, db_session: AsyncSession) -> List[model_type]:
        ...