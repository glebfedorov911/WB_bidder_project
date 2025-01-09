from typing import Dict
from datetime import datetime, timedelta
import uuid

import jwt


class TokenMixin:
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

class TokenEncodeService(TokenMixin):
    def __init__(
        self, data: Dict[str, uuid.UUID], expire_time: int, 
        secret_key: str, algorithm: str
    ) -> None:
        super().__init__(secret_key=secret_key, algorithm=algorithm)
        self.expire_time = expire_time * self._time_multiplier()
        self.data = data

    def _time_multiplier(self) -> int:
        return 1

    def create_token(self) -> str:
        to_encode = self.__create_to_encode_collection()
        return jwt.encode(to_encode, self.secret_key, self.algorithm)
    
    def __create_to_encode_collection(self) -> Dict:
        to_encode = self.data.copy()
        to_encode.update({"exp": self.__get_time_expires_at()})
        return to_encode

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
            algorithm=algorithm
        )

    def _time_multiplier(self) -> int:
        return 60

class RefreshTokenService(TokenEncodeService):
    def __init__(
        self, data: Dict[str, uuid.UUID], expire_time: int,
        secret_key: str, algorithm: str
    ) -> None:
        super().__init__(
            data=data,
            expire_time=expire_time, 
            secret_key=secret_key, 
            algorithm=algorithm
        )

    def _time_multiplier(self) -> int:
        return 24 * 60 * 60

class TokenVerifyService(TokenMixin):
    def __init__(self, token: str, secret_key: str, algorithm: str):
        super().__init__(secret_key=secret_key, algorithm=algorithm)
        self.token = token

    def verify_token(self):
        try:
            return self.__decode_token()
        except Exception as e:
            print(e)

    def __decode_token(self):
        return jwt.decode(self.token, self.secret_key, algorithms=[self.algorithm])