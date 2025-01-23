import uuid
from typing import List, Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..interfaces.repository_interface import IRepository
from ..dependencies.builders import QueryBuilder
from ..dependencies.exceptions import RepositoryException
from core.models.base import Base
from core.models.types.type_operation import TypeOperation
from core.settings import settings

schema_type = TypeVar("S", bound=BaseModel) 
model_type = TypeVar("M", bound=Base)
builder_type = TypeVar("B", bound=QueryBuilder) 


class Repository(IRepository):
    def __init__(
        self, 
        db_session: AsyncSession,
        model: model_type,
        builder: builder_type,
    ) -> None:
        self.db_session = db_session
        self.model = model
        self.builder = builder

    async def create(self, data: schema_type) -> model_type:
        try:
            return await self._add_data_to_table(data=data)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise RepositoryException("Cannot create. Invalid data")

    async def _add_data_to_table(self, data: model_type) -> model_type:
        data_to_table = self.model(**data.model_dump())
        return await self._save_data(data=data_to_table)
    
    async def get(self) -> List[model_type]:
        return await self._get_all_data()

    async def get_by_id(self, id: Optional[uuid.UUID] = None) -> model_type:
        try:
            return await self._get_data_by_id(id=id)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise RepositoryException("Cannot get. Invalid id")
            
    async def update(self, id: uuid.UUID, data: schema_type) -> model_type:
        try:
            return await self._update_data(id=id, data=data)
        except Exception as e:
            raise RepositoryException("Cannot update. Invalid data")

    async def delete(self, id: uuid.UUID) -> bool:
        try:
            self._delete_data(id=id)
            return True
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise RepositoryException("Cannot create. Invalid id")

    async def _update_data(self, id: uuid.UUID, data: schema_type):
        data_from_table = self._ensure_data_exists(await self._get_data_by_id(id=id))
        data_updated = self._update_data_record(data=data, data_from_table=data_from_table)
        return await self._save_data(data=data_updated)

    async def _save_data(self, data: model_type) -> model_type:
        self._add_to_session(data)
        await self._commit()
        return data

    def _add_to_session(self, data: model_type) -> None:
        self.db_session.add(data)

    def _update_data_record(self, data: schema_type, data_from_table: model_type) -> model_type:
        for key, value in data:
            if value is not None:
                setattr(data_from_table, key, value)
        return data_from_table

    async def _delete_data(self, id: uuid.UUID) -> None:
        data = self._ensure_data_exists(await self._get_data_by_id(id=id))
        await self.db_session.delete(data)
        await self._commit()

    async def _commit(self) -> None:
        await self.db_session.commit()

    def _ensure_data_exists(self, data: model_type) -> model_type:
        if data is None:
            raise RepositoryException("Does not exists data")
        return data

    async def _get_all_data(self) -> List[model_type]:
        return await self.builder.execute(self.db_session)

    async def _get_data_by_id(self, id: uuid.UUID) -> Optional[model_type]:
        return await self._get_result_by_condition([
            (self.model.id, id, TypeOperation.EQUAL)
        ])

    async def _get_result_by_condition(self, condition_by_value_and_operation: list[tuple]):
        for condition, value, type_operation in condition_by_value_and_operation:
            self.builder = self.builder.add_condition(condition, value, type_operation)
        result = await self.builder.execute(self.db_session)
        if result:
            return result[0]
        else:
            raise RepositoryException("Cannot found data")