from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from core.settings import settings


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = settings.auth.TOKEN_TYPE

class RefreshTokenCreate(BaseModel):
    token: str
    expires_at: datetime
    user_id: Optional[uuid.UUID] = None

class RefreshTokenUpdate(BaseModel):
    token: Optional[str] = None
    expires_at: Optional[datetime] = None 
    using: Optional[bool] = None
    user_id: Optional[uuid.UUID] = None

class RefreshTokenSchema(BaseModel):
    refresh_token: str