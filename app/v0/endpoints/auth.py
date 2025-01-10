from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.token_service import (
    TokenService, TokenVerifyService,
    AccessTokenService, RefreshTokenService
)
from ..repositories.token_repository import TokenRepository
from ..schemas.token_schema import Token
from ..schemas.user_schema import UserCreate
from core.settings import settings
from core.models.databasehelper import database_helper

from core.models.enum.accountstatus import AccountStatus
from core.models.enum.accountrole import AccountRole

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.get("/test/")
async def test(db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    user = UserCreate(
        firstname="Test",
        lastname="Test",
        patronymic="Test",
        phone="+71234567890",
        email="test@mail.ru",
        password="123456n",
        account_status=AccountStatus.PENDING,
        account_role=AccountRole.DEFAULT_USER,
        is_superuser=False,
        has_subscription=False
    )

    return user