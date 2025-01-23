from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from ..interfaces.repository_interface import IUserRepository
from core.models.types.type_operation import TypeOperation
from ..dependencies.builders import UserBuilder
from .repository import Repository


class UserRepository(Repository, IUserRepository):
    def __init__(
        self, 
        db_session: AsyncSession, 
        model: User = User,
        builder: UserBuilder = UserBuilder()
    ) -> None:
        super().__init__(db_session=db_session, model=model, builder=builder)
    
    async def get_by_phone(self, phone: str) -> None:
        return await self._get_result_by_condition([
            (self.model.phone, phone, TypeOperation.EQUAL)
        ])