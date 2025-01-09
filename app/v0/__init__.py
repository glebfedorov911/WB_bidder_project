from fastapi import APIRouter

from core.settings import settings

from .endpoints.user import router as user_router


router = APIRouter(prefix=settings.api.v0)
router.include_router(user_router)