import uuid

from ..schemas.user_schema import phone_number
from core.models.enum.typecode import TypeCode

from pydantic import BaseModel


class VerCodeCreate(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    type_code: TypeCode = TypeCode.ACCOUNT_CONFIRM
    user_id: uuid.UUID
    code: str

class VerCodeUpdate(BaseModel):
    is_used: bool

class PhoneSchema(BaseModel):
    phone: str = phone_number

class VerificationSMS(PhoneSchema):
    code: str

class RecoveryPassword(VerificationSMS):
    new_password: str
