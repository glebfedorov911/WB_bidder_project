from sqlalchemy.ext.asyncio import AsyncSession

from core.models.verification_codes import VerificationCode
from core.models.enum.typecode import TypeCode
from core.models.types.type_operation import TypeOperation
from ..interfaces.repository_interface import IVerCodeRepository, model_type
from ..dependencies.builders import VerCodeBuilder
from .repository import Repository

import uuid
from datetime import datetime



class VerCodeRepository(Repository, IVerCodeRepository):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: VerificationCode = VerificationCode,
        builder: VerCodeBuilder = VerCodeBuilder()
    ) -> None:
        super().__init__(db_session=db_session, model=model, builder=builder)

    async def get_by_user_id_and_code(self, user_id: uuid.UUID, code: str, type_code: TypeCode) -> model_type:
        return await self._get_result_by_condition([
            (self.model.user_id, user_id, TypeOperation.EQUAL),
            (self.model.code, code, TypeOperation.EQUAL),
            (self.model.is_used, True, TypeOperation.EQUAL),
            (self.model.type_code, type_code, TypeOperation.EQUAL),
            (self.model.expires_at, datetime.utcnow(), TypeOperation.LOWER_OR_EQUAL),
        ])