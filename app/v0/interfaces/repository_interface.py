from typing import TypeVar, List
from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import Base
from ..dependencies.builders import QueryBuilder


schema_type = TypeVar("S", bound=BaseModel) 
model_type = TypeVar("M", bound=Base)
builder_type = TypeVar("B", bound=QueryBuilder) 

class IRepository(ABC):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: model_type, 
        builder: builder_type
    ) -> None:
        ...

    @abstractmethod
    async def create(self, data: schema_type) -> model_type:
        ...

    @abstractmethod
    async def get(self) -> List[model_type]:
        ...

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> model_type:
        ...

    @abstractmethod
    async def update(self, id: uuid.UUID, data: schema_type) -> model_type:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...

class ITokenRepository(IRepository):
    ...

class IUserRepository(IRepository):
    
    @abstractmethod
    async def get_by_phone(self, phone: str) -> model_type:
        ...

class IVerCodeRepository(IRepository):
    
    @abstractmethod
    async def get_by_user_id_and_code(self, user_id: uuid.UUID, code: str) -> model_type:
        ...