from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import uuid 

from sqlalchemy import Enum as SQLEnum, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .mixin import VerificationCodeAndTokenMixin, DateMixin
from .enum.typecode import TypeCode

if TYPE_CHECKING:
    from .user import User


class VerificationCode(DateMixin, VerificationCodeAndTokenMixin, Base):    
    _back_populates = "code"
    _user_id_index = True

    code: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        default=lambda: VerificationCode.calculate_expiration()
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=True)
    type_code: Mapped[TypeCode] = mapped_column(
        SQLEnum(TypeCode), 
        nullable=False,
        default=TypeCode.ACCOUNT_CONFIRM,
    )

    EXPIRES_MINUTE = 30

    @classmethod
    def calculate_expiration(cls) -> datetime:
        return datetime.utcnow() + timedelta(minutes=cls.EXPIRES_MINUTE)