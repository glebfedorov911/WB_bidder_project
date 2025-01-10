from typing import TYPE_CHECKING
from datetime import datetime
import uuid 

from sqlalchemy import Enum as SQLEnum, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .mixin import VerificationCodeAndTokenMixin, DateMixin
from .enum.tokentype import TypeToken

if TYPE_CHECKING:
    from .user import User


class Token(DateMixin, VerificationCodeAndTokenMixin, Base):
    _back_populates = "tokens"
    _user_id_index = True
    
    token: Mapped[str] = mapped_column(String, nullable=False)
    token_type: Mapped[TypeToken] = mapped_column(
        SQLEnum(TypeToken), 
        nullable=False,
        default=TypeToken.ACCESS_TOKEN
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime)