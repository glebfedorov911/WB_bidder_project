from typing import TypeVar, List, Self

from sqlalchemy import select, Result
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..interfaces.builder_interface import IQueryBuilder
from core.models.token import RefreshToken
from core.models.user import User
from core.models.verification_codes import VerificationCode
from core.models.base import Base
from core.models.types.type_operation import TypeOperation


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

    def add_condition(self, column: ColumnElement, value: any, type_operation: str = "e") -> Self:
        if type_operation == TypeOperation.EQUAL:
            self.query = self.query.where(column == value)
        elif type_operation == TypeOperation.GREATER:
            self.query = self.query.where(column < value)
        elif type_operation == TypeOperation.GREATER_OR_EQUAL:
            self.query = self.query.where(column <= value)
        elif type_operation == TypeOperation.LOWER:
            self.query = self.query.where(column > value)
        elif type_operation == TypeOperation.LOWER_OR_EQUAL:
            self.query = self.query.where(column >= value)
        return self

    async def execute(self, db_session: AsyncSession) -> List[model_type]:
        result: Result = await db_session.execute(self.query)
        self.query = self.__query_to_start()
        return result.scalars().all()

    def __query_to_start(self):
        return select(self.model)

class TokenBuilder(QueryBuilder):
    def __init__(self, model: RefreshToken = RefreshToken):
        super().__init__(model=model)

class UserBuilder(QueryBuilder):
    def __init__(self, model: User = User):
        super().__init__(model=model)

class VerCodeBuilder(QueryBuilder):
    def __init__(self, model: VerificationCode = VerificationCode):
        super().__init__(model=model)