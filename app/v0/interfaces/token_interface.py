from typing import TypeVar, List
from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import Base

T = TypeVar("T", bound=BaseModel) 
M = TypeVar("M", bound=Base) 

class IRepository(ABC):
    def __init__(self, db_session: AsyncSession) -> None:
        ...

    @abstractmethod
    def create(self, data: T) -> M:
        ...

    @abstractmethod
    def get(self) -> List[M]:
        ...

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> M:
        ...

    @abstractmethod
    def update(self, id: uuid.UUID, data: T) -> M:
        ...

    @abstractmethod
    def delete(self, id: uuid.UUID) -> bool:
        ...

class ITokenRepository(IRepository):
    ...