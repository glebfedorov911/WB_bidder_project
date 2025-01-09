from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenCreate(BaseModel):
    token: str
    type_token: str
    expires_at: datetime
    user_id: int

class TokenUpdate(BaseModel):
    token: Optional[str] = None
    type_token: Optional[str] = None
    expires_at: Optional[datetime] = None 
    user_id: Optional[int] = None