from .builder import QueryBuilder
from core.models.token import Token


class TokenBuilder(QueryBuilder):
    def __init__(self, model: Token):
        super().__init__(model=model)