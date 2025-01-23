from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.token_service import TokenVerifyService, get_token_verify_service
from ..repositories.user_repository import UserRepository
from ..interfaces.repository_interface import IUserRepository
from ..schemas.user_schema import UserCreate, UserUpdate, AccountStatusSchema, UserRead, UserBase
from ..schemas.verificationcode_schema import RecoveryPassword
from ..dependencies.password_hasher import PasswordHasher
from ..dependencies.exceptions import (
    CustomHTTPException, HTTP405Exception, HTTP404Exception, 
    HTTP500Exception, HTTP403Exception, HTTP401Exception,
    RepositoryException, HTTP400Exception
)
from core.models.user import User
from core.models.databasehelper import database_helper
from core.models.enum.accountstatus import AccountStatus
from core.settings import settings

import uuid


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/auth/login")

class UserServiceMixin:
    def __init__(
        self, 
        user_repository: IUserRepository,        
    ):
        self.user_repository = user_repository 

    async def get_user_by_phone(self, phone: str) -> User:
        try:
            user = await self.user_repository.get_by_phone(phone=phone)
            return user
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception("Not found user with this phone number")

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
            return await self.__create_new_user_with_hash_password(user_schema=user_create)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception("This phone or email already used")
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP500Exception('Internal Server Error')

    async def change_password(self, user: User, recovery_password: RecoveryPassword) -> User:
        try:
            return await self.__change_password(user=user, recovery_password=recovery_password)
        except CustomHTTPException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP405Exception(e)
        except ValueError as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception(e)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP500Exception('Internal Server Error')

    async def __change_password(self, user: User, recovery_password: RecoveryPassword) -> User:
        phone = recovery_password.phone
        password = recovery_password.new_password

        user_update_hash_password = await self._get_user_update_schema_with_hash_password(password=password)

        return await self.user_repository.update(id=user.id, data=user_update_hash_password)

    async def _get_user_update_schema_with_hash_password(self, password: str):
        user_update = UserUpdate(
            password=password
        )
        return self.__set_hash_password(password=password, user_schema=user_update)

    async def __create_new_user_with_hash_password(self, user_schema: UserBase) -> User:
        user_schema = self.__set_hash_password(password=user_schema.password, user_schema=user_schema)
        user: User = await self.user_repository.create(user_schema)
        return user

    def __set_hash_password(self, password: str, user_schema: UserBase) -> UserBase:
        user_schema.password = self.password_hasher.hash_password(password=password)
        return user_schema
    
    async def set_account_status(self, user_id: uuid.UUID, account_status: str):
        try:
            acc_status = AccountStatusSchema(
                account_status=account_status
            )
            return await self.user_repository.update(id=user_id, data=acc_status)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP405Exception(e)


class UserQueryService(UserServiceMixin):
    def __init__(self, user_repository: IUserRepository):
        super().__init__(user_repository=user_repository)

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        try:
            return await self.user_repository.get_by_id(id=id)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP405Exception(e)

class UserAuthService:
    def __init__(self, query_service: UserQueryService, password_hasher: PasswordHasher):
        self.query_service = query_service
        self.password_hasher = password_hasher

    async def authenticate(self, phone: str, password: str) -> bool:
        try:
            user = await self.query_service.get_user_by_phone(phone=phone)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception('Invalid phone number')
        if not self.__valid_password(password=password, hash_password=user.password):
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception('Invalid password')
        return user

    def __valid_password(self, password, hash_password) -> bool:
        return self.password_hasher.verify_password(plain_password=password, hashed_password=hash_password)

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

def get_auth_user_service(
    user_query_service: UserQueryService = Depends(get_user_query_service),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> UserAuthService:
    return UserAuthService(query_service=user_query_service, password_hasher=password_hasher)

async def get_current_user(
    request: Request,
    token_verify: TokenVerifyService = Depends(get_token_verify_service), 
    token: str = Depends(oauth2_scheme),
    user_manager: UserQueryService = Depends(get_user_query_service)
) -> User:
    credential_exception = HTTP401Exception("Could not validate credentials")
    try:
        payload = token_verify.verify_token(token=token, request=request)
        user_id: uuid.UUID = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise credential_exception
    except InvalidTokenError as e:
        settings.statberry_logger.get_loger().error(e)
        raise credential_exception
    except Exception as e:
        settings.statberry_logger.get_loger().error(e)
        raise HTTP405Exception("Token Invalid")
    user = await user_manager.get_user_by_id(id=user_id)
    if user is None:
        raise credential_exception
    return user