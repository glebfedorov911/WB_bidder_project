from typing import TYPE_CHECKING
from datetime import datetime, timedelta
import uuid 

from sqlalchemy import Enum as SQLEnum, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .mixin import VerificationCodeAndTokenMixin, DateMixin
from .enum.tokentype import TypeToken
from core.settings import settings

if TYPE_CHECKING:
    from .user import User


class RefreshToken(DateMixin, VerificationCodeAndTokenMixin, Base):
    _back_populates = "tokens"
    _user_id_index = True
    
    token: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    using: Mapped[bool] = mapped_column(Boolean, default=True)