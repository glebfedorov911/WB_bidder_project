from typing import Dict, Tuple, Type
from datetime import datetime, timedelta
import uuid

import jwt
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from hashlib import sha256

from ..interfaces.repository_interface import ITokenRepository
from ..interfaces.token_creator_interface import ITokenCreator
from ..schemas.token_schema import RefreshTokenCreate, RefreshTokenUpdate
from ..dependencies.jwt_token_creator import JWTTokenCreator
from ..dependencies.encoder import Encoder, get_encoder
from ..repositories.token_repository import TokenRepository
from ..dependencies.exceptions import (
    CustomHTTPException, HTTP405Exception, HTTP404Exception, 
    HTTP500Exception, HTTP403Exception, HTTP401Exception, RepositoryException
)
from core.models.token import RefreshToken
from core.models.databasehelper import database_helper
from core.settings import settings


class TokenMixin:
    def __init__(self, token_creator: ITokenCreator):
        self.token_creator = token_creator

class TokenEncoderMixin:
    def __init__(self, encoder: Encoder):
        self.encoder = encoder

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

class TokenVerifyService(TokenMixin, TokenEncoderMixin):
    def __init__(self, token_creator: ITokenCreator, encoder: Encoder):
        TokenMixin.__init__(self=self, token_creator=token_creator)
        TokenEncoderMixin.__init__(self=self, encoder=encoder) 

    def verify_token(self, token: str, request: Request):
        try:
            payload = self.__decode_token(token=token)
            self.__check_user_agent(user_agent=request.headers.get("user-agent"), payload=payload)
            
            return payload
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP403Exception("Invalid token")

    def __check_user_agent(self, user_agent: str, payload: dict):
        if self.encoder.encode(user_agent) != payload.get('user_agent'):
            raise HTTP405Exception("Bad Auth")

    def __decode_token(self, token: str) -> dict:
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

class TokenManagerService:
    def __init__(self, token_repository: ITokenRepository):
        self.token_repository = token_repository        

    async def set_token_inactive(self, encode_refresh_token: bytes):
        try:
            token: RefreshToken = await self.__get_token_by_encode(encode_refresh_token=encode_refresh_token)
            data = RefreshTokenUpdate(
                using=False
            )
            return await self.token_repository.update(id=token.id, data=data)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception("Token not found")
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP405Exception("Token already not active")

    async def __get_token_by_encode(self, encode_refresh_token: bytes):
        try:
            return await self.token_repository.get_token_by_encode(encode_refresh_token=encode_refresh_token)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception("Token not found")

class TokenEncodeService(TokenEncoderMixin):

    def __init__(self, encoder: Encoder):
        super().__init__(encoder=encoder)

    def encode_token(self, token: str):
        return self.encoder.encode(data=token)

def get_jwt_token_creator():
    return JWTTokenCreator(secret_key=settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM)

def get_token_fabric_service(token_creator: ITokenCreator = Depends(get_jwt_token_creator)):
    return TokenFabricService(token_creator=token_creator)

def get_token_repository(db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    return TokenRepository(db_session=db_session)

def get_token_verify_service(
    token_creator: ITokenCreator = Depends(get_jwt_token_creator),
    encoder: Encoder = Depends(get_encoder)
):
    return TokenVerifyService(token_creator=token_creator, encoder=encoder)

def get_token_encode_service(
    encoder: Encoder = Depends(get_encoder)
) -> TokenEncodeService:
    return TokenEncodeService(encoder=encoder)

def get_token_manager_service(token_repo: ITokenRepository = Depends(get_token_repository)) -> TokenManagerService:
    return TokenManagerService(token_repository=token_repo)