from typing import Dict, Tuple
from datetime import datetime, timedelta
import uuid

import jwt

from ..interfaces.repository_interface import ITokenRepository
from ..schemas.token_schema import TokenCreate
from core.models.token import Token
from core.models.enum.tokentype import TypeToken


class TokenMixin:
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

class TokenEncodeService(TokenMixin):
    def __init__(
        self, data: Dict[str, uuid.UUID], expire_time: int, 
        secret_key: str, algorithm: str, token_type: TypeToken
    ) -> None:
        super().__init__(secret_key=secret_key, algorithm=algorithm)
        self.expire_time = expire_time * self._time_multiplier()
        self.data = data
        self.token_type = token_type

    def _time_multiplier(self) -> int:
        return 1

    def create_token_and_expire_time(self) -> Tuple[str, datetime]:
        to_encode, expire_time = self._create_to_encode_collection()
        return jwt.encode(to_encode, self.secret_key, self.algorithm), expire_time
    
    def _create_to_encode_collection(self) -> Tuple[Dict, datetime]:
        to_encode = self.data.copy()
        expire_time = self.__get_time_expires_at()
        to_encode.update({"exp": expire_time})
        return to_encode, expire_time

    def __get_time_expires_at(self) -> datetime:
        return datetime.utcnow() + timedelta(seconds=self.expire_time)

class AccessTokenService(TokenEncodeService):
    def __init__(
        self, data: Dict[str, uuid.UUID], expire_time: int, 
        secret_key: str, algorithm: str
    ) -> None:
        super().__init__(
            data=data,
            expire_time=expire_time, 
            secret_key=secret_key, 
            algorithm=algorithm,
            token_type=TypeToken.ACCESS_TOKEN
        )
    
    def _time_multiplier(self) -> int:
        return 60

class RefreshTokenService(TokenEncodeService):
    def __init__(
        self, data: Dict[str, uuid.UUID], expire_time: int,
        secret_key: str, algorithm: str, 
    ) -> None:
        super().__init__(
            data=data,
            expire_time=expire_time, 
            secret_key=secret_key, 
            algorithm=algorithm,
            token_type=TypeToken.REFRESH_TOKEN
        )

    def _time_multiplier(self) -> int:
        return 24 * 60 * 60

class TokenVerifyService(TokenMixin):
    def __init__(self, secret_key: str, algorithm: str):
        super().__init__(secret_key=secret_key, algorithm=algorithm)

    def verify_token(self, token: str):
        try:
            return self.__decode_token(token=token)
        except Exception as e:
            print(e)

    def __decode_token(self, token: str):
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

class TokenService:
    def __init__(
        self,
        token_repository: ITokenRepository,
        type_token_service: TokenEncodeService,
        token_verifier: TokenVerifyService,
    ) -> None:
        self.token_repository = token_repository
        self.type_token_service = type_token_service
        self.token_verifier = token_verifier

    async def get_token(self, user_id: uuid.UUID) -> Token:
        token, expire_time = self.type_token_service.create_token_and_expire_time()

        data = TokenCreate(
            token=token,
            token_type=self.type_token_service.token_type,
            expires_at=expire_time,
            user_id=user_id
        )

        return await self.token_repository.create(data=data)

    def verify_token(self, token: str) -> dict:
        return self.token_verifier.verify_token(token=token)