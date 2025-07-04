from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import RefreshToken
from ..interfaces.repository_interface import ITokenRepository
from ..dependencies.builders import TokenBuilder
from .repository import Repository
from core.models.types.type_operation import TypeOperation


class TokenRepository(Repository, ITokenRepository):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: RefreshToken = RefreshToken,
        builder: TokenBuilder = TokenBuilder()
    ) -> None:
        super().__init__(db_session=db_session, model=model, builder=builder)

    async def get_token_by_encode(self, encode_refresh_token: bytes) -> RefreshToken:
        return await self._get_result_by_condition([
            (self.model.token, encode_refresh_token, TypeOperation.EQUAL),
            (self.model.using, True, TypeOperation.EQUAL)
        ])