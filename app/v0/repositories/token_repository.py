import uuid
from typing import List

from fastapi import Depends
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import Token
from core.models.databasehelper import database_helper
from ..interfaces.token_interface import ITokenRepository
from ..schemas.token_schema import TokenCreate, TokenUpdate
from ..builders.token_builder import TokenBuilder

#УДАЛИТЬ ЭТОТ КОМЕНТ
#ИСПРАВИТЬ ЭТОТ КОД
#УБРАТЬ EXCEPTION, ДОБАВИТЬ НОРМ ОБРАБОТКУ
#СОБЛЮДАТЬ ПРИНЦИПЫ DRY, KISS, SOLID,
#ДОПИСАТЬ АВТОРИЗАЦИЮ
#ВЫНЕСТИ ВСЕ TYPEVAR В ОТДЕЛЬНЫЙ ФАЙЛ В КОТОРОМ БУДУ ХРАНИТЬСЯ ТИПВ

class TokenRepository(ITokenRepository):
    def __init__(
        self, db_session: AsyncSession = Depends(database_helper.async_session_depends)
    ) -> None:
        self.db_session = db_session
        self.model = Token
        self.builder = TokenBuilder(self.model)

    async def create(self, data: TokenCreate) -> Token:
        try:
            return await self.__add_new_token(data=data)
        except Exception as e:
            print(e)

    async def update(self, id: uuid.UUID, data: TokenUpdate) -> Token:
        try:
            return self.__update_token(id=id, data=data)
        except Exception as e:
            print(e)

    async def __update_token(self, id: uuid.UUID, data: TokenUpdate):
        token = self.__check_exist_token(self.get_by_id(id=id))
        token_updated = self.__update_token_record(data=data, token=token)
        return await self.__add_and_commit_data(data=token_updated)

    async def __add_new_token(self, data: Token) -> Token:
        token = self.model(**data.model_dump())
        return self.__add_and_commit_data(data=token)

    async def __add_and_commit_data(self, data: Token) -> Token:
        self.__add_to_session(data)
        await self.__commit()
        return data

    def __add_to_session(self, data: Token) -> None:
        self.db_session.add(data)

    async def __commit(self) -> None:
        await self.db_session.commit()

    def __update_token_record(self, data: TokenUpdate, token: Token) -> Token:
        for key, value in data:
            if value:
                setattr(token, key, value)
        return token

    async def get_by_id(self, id: uuid.UUID) -> Token:
        self.builder = self.builder.add_condition(self.model.id, id)
        return await self.__execute_builder()[0]

    async def get(self) -> List[Token]:
        return await self.__execute_builder()

    async def __execute_builder(self) -> List[Token]:
        return await self.builder.execute(self.db_session)

    async def delete(self, id: uuid.UUID) -> bool:
        try:
            self.__delete_token(id=id)
            return True
        except Exception as e:
            print(e)

    async def __delete_token(self, id: uuid.UUID) -> None:
        token = self.__check_exist_token(self.get_by_id(id=id))
        await self.db_session.delete(token)
        await self.__commit()

    def __check_exist_token(self, token: Token) -> None:
        if token is None:
            raise ValueError("Token does not exists")