from typing import Optional
from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, Field

from core.models.enum.accountrole import AccountRole
from core.models.enum.accountstatus import AccountStatus
from core.models.enum.subscriptionstatus import SubscriptionStatus
from core.settings import settings


phone_number = Field(..., pattern=r"^\+?\d{10,15}$")

class UserBase(BaseModel):

    class Config:
        arbitrary_types_allowed = True

class UserCreate(UserBase):
    firstname: str
    lastname: str 
    patronymic: Optional[str] = None
    phone: str = phone_number
    email: Optional[EmailStr] = None
    password: bytes
    account_status: Optional[AccountStatus] = AccountStatus.PENDING
    account_role: Optional[AccountRole] = AccountRole.DEFAULT_USER
    is_superuser: bool = False
    has_subscription: bool = False
    subscription_active_until: Optional[datetime] = None

class UserUpdate(UserBase):
    firstname: Optional[str] = None
    lastname: Optional[str] = None 
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[bytes] = None
    account_status: Optional[AccountStatus] = None
    account_role: Optional[AccountRole] = None
    is_superuser: Optional[bool] = None
    has_subscription: Optional[bool] = None
    subscription_active_until: Optional[datetime] = None