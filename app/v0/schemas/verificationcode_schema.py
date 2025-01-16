import uuid

from pydantic import BaseModel


class VerCodeCreate(BaseModel):
    user_id: uuid.UUID
    code: str

class VerCodeUpdate(BaseModel):
    is_used: bool