from sqlalchemy.ext.asyncio import AsyncSession

from core.models.verification_codes import VerificationCode
from ..interfaces.repository_interface import IVerCodeRepository
from ..dependencies.builders import VerCodeBuilder
from .repository import Repository


class VerCodeRepository(Repository, IVerCodeRepository):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: VerificationCode = VerificationCode,
        builder: VerCodeBuilder = VerCodeBuilder()
    ) -> None:
        super().__init__(db_session=db_session, model=model, builder=builder)