from typing import Dict, Tuple, Type
from datetime import datetime, timedelta
import uuid

import jwt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from hashlib import sha256

from ..interfaces.repository_interface import ITokenRepository
from ..interfaces.token_creator_interface import ITokenCreator
from ..schemas.token_schema import RefreshTokenCreate
from ..dependencies.jwt_token_creator import JWTTokenCreator
from ..repositories.token_repository import TokenRepository
from core.models.token import RefreshToken
from core.models.enum.tokentype import TypeToken
from core.models.databasehelper import database_helper
from core.settings import settings


class TokenMixin:
    def __init__(self, token_creator: ITokenCreator):
        self.token_creator = token_creator

class TokenCreatorService(TokenMixin):
    def __init__(
        self, 
        data: Dict[str, str], 
        expire_time: int, 
        token_creator: ITokenCreator
    ) -> None:
        super().__init__(token_creator=token_creator)
        self.data = data
        self.expire_time = expire_time

    def create_token_and_expire_time(self) -> Tuple[str, datetime]:
        to_encode, expire_time = self._create_to_encode_collection()
        return self.token_creator.encode(to_encode), expire_time
    
    def _create_to_encode_collection(self) -> Tuple[Dict, datetime]:
        to_encode = self.data.copy()
        expire_time = self._get_expire_time()
        to_encode.update({"exp": expire_time})
        return to_encode, expire_time

    def _get_expire_time(self):
        return datetime.now() + timedelta(seconds=self.expire_time)

class AccessTokenService(TokenCreatorService):
    def __init__(
        self, data: Dict[str, str], expire_time: int, token_creator: ITokenCreator
    ) -> None:
        super().__init__(
            data=data,
            expire_time=expire_time, 
            token_creator=token_creator
        )

class RefreshTokenService(TokenCreatorService):
    def __init__(
        self, data: Dict[str, str], expire_time: int, token_creator: ITokenCreator
    ) -> None:
        super().__init__(
            data=data,
            expire_time=expire_time, 
            token_creator=token_creator
        )

class TokenVerifyService(TokenMixin):
    def __init__(self, token_creator: ITokenCreator):
        super().__init__(token_creator=token_creator)

    def verify_token(self, token: str):
        try:
            return self.__decode_token(token=token)
        except Exception as e:
            print(e)

    def __decode_token(self, token: str):
        return self.token_creator.decode(token)

class TokenServiceFactory:
    def __init__(self, token_creator: ITokenCreator):
        self.token_creator = token_creator

    def create_access_token_service(self, expire_time: int, data: Dict[str, str]) -> AccessTokenService:
        return AccessTokenService(
            data=data,
            expire_time=expire_time,
            token_creator=self.token_creator
        )

    def create_refresh_token_service(self, expire_time: int, data: Dict[str, str]) -> AccessTokenService:
        return RefreshTokenService(
            data=data,
            expire_time=expire_time,
            token_creator=self.token_creator
        )

class TokenFabricService:
    def __init__(self, token_creator: ITokenCreator):
        self.token_creator = token_creator
        self.token_service_factory = TokenServiceFactory(token_creator=self.token_creator)

    def create_access_token_service(self, expire_time: int, data: Dict[str, str]) -> AccessTokenService:
        return self.token_service_factory.create_access_token_service(
            expire_time=expire_time, data=data
        )
    
    def create_refresh_token_service(self, expire_time: int, data: Dict[str, str]) -> RefreshTokenService:
        return self.token_service_factory.create_refresh_token_service(
            expire_time=expire_time, data=data
        )

class TokenService:
    def __init__(self, token_fabric: TokenFabricService, expire_access_time: int, expire_refresh_time: int, data: dict):
        self.token_fabric = token_fabric
        self.expire_access_time = expire_access_time
        self.expire_refresh_time = expire_refresh_time
        self.data = data
        self.access_token_service = self.token_fabric.create_access_token_service(expire_time=self.expire_access_time, data=self.data)
        self.refresh_token_service = self.token_fabric.create_refresh_token_service(expire_time=self.expire_refresh_time, data=self.data)

    def create_tokens(self) -> tuple[str, datetime, str, datetime]:
        access_token, expire_access = self.access_token_service.create_token_and_expire_time()
        refresh_token, expire_refresh = self.refresh_token_service.create_token_and_expire_time()

        return access_token, expire_access, refresh_token, expire_refresh

class TokenEncodeService:

    @staticmethod
    def encode_token(token: str):
        return sha256(token.encode()).hexdigest()

def get_jwt_token_creator():
    return JWTTokenCreator(secret_key=settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM)

def get_token_fabric_service(token_creator: ITokenCreator = Depends(get_jwt_token_creator)):
    return TokenFabricService(token_creator=token_creator)

def get_token_repository(db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    return TokenRepository(db_session=db_session)

def get_token_verify_service(token_creator: ITokenCreator = Depends(get_jwt_token_creator)):
    return TokenVerifyService(token_creator=token_creator)

def get_token_encode_service():
    return TokenEncodeService()