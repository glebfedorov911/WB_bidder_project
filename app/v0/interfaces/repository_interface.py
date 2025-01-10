from typing import TypeVar, List
from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import Base
from ..dependencies.builders import QueryBuilder
from ..dependencies.types import schema_type, builder_type, model_type

class IRepository(ABC):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: model_type, 
        builder: builder_type
    ) -> None:
        ...

    @abstractmethod
    def create(self, data: Schema) -> model_type:
        ...

    @abstractmethod
    def get(self) -> List[model_type]:
        ...

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> model_type:
        ...

    @abstractmethod
    def update(self, id: uuid.UUID, data: Schema) -> model_type:
        ...

    @abstractmethod
    def delete(self, id: uuid.UUID) -> bool:
        ...

class ITokenRepository(IRepository):
    ...