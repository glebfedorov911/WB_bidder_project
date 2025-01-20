import uuid

from ..schemas.user_schema import phone_number

from pydantic import BaseModel


class VerCodeCreate(BaseModel):
    user_id: uuid.UUID
    code: str

class VerCodeUpdate(BaseModel):
    is_used: bool

class PhoneSchema(BaseModel):
    phone: str = phone_number

class VerificationSMS(BaseModel):
    phone: str = phone_number
    code: str