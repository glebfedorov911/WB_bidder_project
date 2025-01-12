from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from core.settings import settings


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = settings.auth.TOKEN_TYPE

class TokenCreate(BaseModel):
    token: str
    token_type: str
    expires_at: datetime
    user_id: Optional[uuid.UUID] = None

class TokenUpdate(BaseModel):
    token: Optional[str] = None
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None 
    user_id: Optional[uuid.UUID] = None