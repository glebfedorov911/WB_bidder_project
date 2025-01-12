from typing import Optional
import uuid

from pydantic import BaseModel


class VerCodeCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    is_used: bool = True
    code: str

class VerCodeUpdate(BaseModel):
    is_used: Optional[bool] = None