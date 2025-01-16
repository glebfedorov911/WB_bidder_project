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
        data.password = bytes(self.password_hasher.hash_password(data.password).encode("utf-8"))
        return await self.user_repository.create(data)

    async def valid(self, user_id, password):
        user = await self.user_repository.get_by_id(id=user_id)
        return self.password_hasher.verify_password(plain_password=password, hashed_password=user.password)
