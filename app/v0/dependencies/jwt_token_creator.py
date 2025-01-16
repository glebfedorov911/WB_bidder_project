from typing import Dict

import jwt

from ..interfaces.token_creator_interface import ITokenCreator


class JWTTokenCreator(ITokenCreator):
    def __init__(self, secret_key: str, algorithm: str):
        self.__algorithm = algorithm
        self.__secret_key = secret_key

    def encode(self, encode_data: dict) -> str:
        return jwt.encode(encode_data, self.__secret_key, self.__algorithm)
    
    def decode(self, token: str) -> Dict[str, any]:
        return jwt.decode(token, self.__secret_key, algorithms=[self.__algorithm])