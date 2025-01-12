from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.token_service import (
    TokenService, TokenVerifyService,
    AccessTokenService, RefreshTokenService
)
from ..repositories.token_repository import TokenRepository
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService
from ..schemas.token_schema import Token
from ..schemas.user_schema import UserCreate
from ..dependencies.password_hasher import PasswordHasher
from core.settings import settings
from core.models.databasehelper import database_helper

from core.models.enum.accountstatus import AccountStatus
from core.models.enum.accountrole import AccountRole

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/test/")
async def test(user_in: UserCreate, db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    repo = UserRepository(db_session=db_session)
    hasher = PasswordHasher()
    service = UserService(user_repository=repo, password_hasher=hasher)

    return await service.create(data=user_in)