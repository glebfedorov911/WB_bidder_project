from typing import Optional
from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError

from core.models.enum.accountrole import AccountRole
from core.models.enum.accountstatus import AccountStatus
from core.models.enum.subscriptionstatus import SubscriptionStatus
from core.settings import settings
from ..dependencies.exceptions import CustomHTTPException
from ..dependencies.validators import validate_password


phone_number = Field(..., pattern=r"^\+?\d{10,15}$")

class UserBase(BaseModel):

    class Config:
        arbitrary_types_allowed = True

class UserCreate(UserBase):
    firstname: str
    lastname: str 
    patronymic: Optional[str] = None
    phone: str = phone_number
    email: EmailStr
    password: str | bytes

    @field_validator("password")
    def validate_password(cls, value):
        return validate_password(value)

class UserUpdate(UserBase):
    firstname: Optional[str] = None
    lastname: Optional[str] = None 
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str | bytes] = None

    @field_validator("password")
    def validate_password(cls, value):
        return validate_password(value)

class UserRead(UserBase):
    firstname: str
    lastname: str 
    patronymic: str
    phone: str = phone_number
    email: EmailStr | None = None
    account_status: AccountStatus

class AccountStatusSchema(UserBase):
    account_status: AccountStatus