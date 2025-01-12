from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserCreate, UserUpdate
from ..dependencies.password_hasher import PasswordHasher
from core.models.user import User



class UserService:
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository 
        self.password_hasher = password_hasher
        
    async def create(self, data: UserCreate):

        return await self.user_repository.create(data)