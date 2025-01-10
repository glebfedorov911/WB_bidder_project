from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.token_service import (
    TokenService, TokenVerifyService,
    AccessTokenService, RefreshTokenService
)
from ..repositories.token_repository import TokenRepository
from ..schemas.token_schema import Token
from core.settings import settings
from core.models.databasehelper import database_helper


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.get("/token/")
async def token(db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    tvs = TokenVerifyService(
        secret_key=settings.auth.SECRET_KEY,
        algorithm=settings.auth.ALGORITHM
    )
    ats = AccessTokenService(
        data={"312bb66c-94bb-4532-aab4-32d553507eb9": "test"},
        expire_time=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=settings.auth.SECRET_KEY,
        algorithm=settings.auth.ALGORITHM
    )
    rts = RefreshTokenService(
        data={"312bb66c-94bb-4532-aab4-32d553507eb9": "test"},
        expire_time=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS,
        secret_key=settings.auth.SECRET_KEY,
        algorithm=settings.auth.ALGORITHM
    )
    repo = TokenRepository(
        db_session=db_session,
    )
    ts1 = TokenService(
        token_repository=repo,
        type_token_service=ats,
        token_verifier=tvs
    )
    ts2 = TokenService(
        token_repository=repo,
        type_token_service=rts,
        token_verifier=tvs
    ) 
    return Token(
        access_token= (await ts1.get_token("312bb66c-94bb-4532-aab4-32d553507eb9")).token,
        refresh_token= (await ts2.get_token("312bb66c-94bb-4532-aab4-32d553507eb9")).token
    )