from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.databasehelper import database_helper
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..dependencies.password_hasher import PasswordHasher
from ..schemas.user_schema import UserCreate

import uuid


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/test/")
async def test(password: str, user_id: uuid.UUID, db_session: AsyncSession = Depends(database_helper.async_session_depends)):
    repo = UserRepository(db_session=db_session)
    hasher = PasswordHasher()
    service = UserService(user_repository=repo, password_hasher=hasher)
    return await service.valid(user_id=user_id, password=password)