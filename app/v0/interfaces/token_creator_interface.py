from abc import ABC, abstractmethod


class ITokenCreator(ABC):

    @abstractmethod
    def encode(self, encode_data: dict) -> str:
        ...

    @abstractmethod
    def decode(self, token: str) -> Dict[str, any]:
        ...