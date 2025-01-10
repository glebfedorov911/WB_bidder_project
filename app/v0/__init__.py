from fastapi import APIRouter

from core.settings import settings

from .endpoints.auth import router as auth_router


router = APIRouter(prefix=settings.api.v0)
router.include_router(auth_router)