from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from ..interfaces.repository_interface import IUserRepository
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