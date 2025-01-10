from typing import TypeVar, List, Self

from sqlalchemy import select, Result
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..interfaces.builder_interface import IQueryBuilder
from core.models.token import Token
from core.models.base import Base


schema_type = TypeVar("S", bound=BaseModel) 
model_type = TypeVar("M", bound=Base)

class QueryBuilder(IQueryBuilder):
    def __init__(self, model: model_type):
        self.model = model
        self.query = self.__query_to_start()

    def limit(self, value_limit: int) -> Self:
        self.query = self.query.limit(limit=value_limit)
        return self

    def order_by(self, columns: List[ColumnElement]) -> Self:
        self.query = self.query.order_by(*columns)
        return self

    def add_condition(self, column: ColumnElement, value: any) -> Self:
        self.query = self.query.where(column == value)
        return self

    async def execute(self, db_session: AsyncSession) -> List[model_type]:
        result: Result = await session.execute(self.query)
        self.query = self.__query_to_start()
        return result.scalars().all()

    def __query_to_start(self):
        return select(self.model)

class TokenBuilder(QueryBuilder):
    def __init__(self, model: Token = Token):
        super().__init__(model=model)