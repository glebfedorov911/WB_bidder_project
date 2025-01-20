from sqlalchemy.ext.asyncio import AsyncSession

from core.models.token import RefreshToken
from ..interfaces.repository_interface import ITokenRepository
from ..dependencies.builders import TokenBuilder
from .repository import Repository


class TokenRepository(Repository, ITokenRepository):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: RefreshToken = RefreshToken,
        builder: TokenBuilder = TokenBuilder()
    ) -> None:
        super().__init__(db_session=db_session, model=model, builder=builder)