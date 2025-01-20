from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.token_service import TokenVerifyService, get_token_verify_service
from ..repositories.user_repository import UserRepository
from ..interfaces.repository_interface import IUserRepository
from ..schemas.user_schema import UserCreate, UserUpdate, AccountStatusSchema
from ..dependencies.password_hasher import PasswordHasher
from ..dependencies.exceptions import RepositoryException, CustomHTTPException
from core.models.user import User
from core.models.databasehelper import database_helper
from core.models.enum.accountstatus import AccountStatus

import uuid


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/auth/login")

class UserServiceMixin:
    def __init__(
        self, 
        user_repository: IUserRepository,        
    ):
        self.user_repository = user_repository 
    
    async def get_user_by_id(self, id: uuid.UUID) -> User:
        try:
            return await self.user_repository.get_by_id(id=id)
        except RepositoryException as e:
            raise CustomHTTPException(e)

class UserManagerService(UserServiceMixin):
    def __init__(
        self, 
        user_repository: IUserRepository,
        password_hasher: PasswordHasher,
    ):
        super().__init__(user_repository=user_repository)
        self.password_hasher = password_hasher

    async def create(self, user_create: UserCreate) -> User:
        try:
            return await self.__create_new_user_with_hash_password(user_create=user_create)
        except RepositoryException as e:
            raise CustomHTTPException("This phone or email already used")
        except Exception as e:
            raise CustomHTTPException(e)

    async def __create_new_user_with_hash_password(self, user_create: UserCreate) -> User:
        user_create = self.__set_hash_password(password=user_create.password, user_create=user_create)
        user: User = await self.user_repository.create(user_create)
        return user

    def __set_hash_password(self, password: str, user_create: UserCreate) -> UserCreate:
        user_create.password = self.password_hasher.hash_password(password=password)
        return user_create
    
    async def set_account_status(self, user_id: uuid.UUID, account_status: str):
        acc_status = AccountStatusSchema(
            account_status=account_status
        )
        return await self.user_repository.update(id=user_id, data=acc_status)

class UserQueryService(UserServiceMixin):
    def __init__(self, user_repository: IUserRepository):
        super().__init__(user_repository=user_repository)

    async def get_user_by_phone(self, phone: str) -> User:
        try:
            return await self.user_repository.get_by_phone(phone=phone)
        except RepositoryException as e:
            raise CustomHTTPException(e)

class UserService:
    def __init__(self, query_service: UserQueryService, password_hasher: PasswordHasher):
        self.query_service = query_service
        self.password_hasher = password_hasher

    async def authenticate(self, phone: str, password: str) -> bool:
        user = self.query_service.get_user_by_phone(phone=phone)
        if not user:
            return False
        if not self.__valid_password(password=password, hash_password=user.password):
            return False
        return True

    def __valid_password(self, password, hash_password) -> bool:
        return self.password_hasher.verify_password(plain_password=password, hashed_password=user.password)

def get_user_repository(db_session: AsyncSession = Depends(database_helper.async_session_depends)) -> IUserRepository:
    return UserRepository(db_session=db_session)

def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()

def get_user_manager_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> UserManagerService:
    return UserManagerService(user_repository=user_repository, password_hasher=password_hasher)

def get_user_query_service(user_repository: IUserRepository = Depends(get_user_repository)) -> UserQueryService:
    return UserQueryService(user_repository=user_repository)

async def get_current_user(
    token_verify: TokenVerifyService = Depends(get_token_verify_service), 
    token: str = Depends(oauth2_scheme),
    user_manager: UserQueryService = Depends(get_user_query_service)
) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = token_verify.verify_token(token=token)
        user_id: uuid.UUID = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise credential_exception
    except InvalidTokenError:
        raise credential_exception
    user = await user_manager.get_user_by_id(id=user_id)
    if user is None:
        raise credential_exception
    return user