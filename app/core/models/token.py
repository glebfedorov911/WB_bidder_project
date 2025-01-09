from typing import TYPE_CHECKING
from datetime import datetime
import uuid 

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .mixin import VerificationCodeAndTokenMixin, DateMixin

if TYPE_CHECKING:
    from .user import User


class Token(DateMixin, VerificationCodeAndTokenMixin, Base):
    _back_populates = "tokens"
    _user_id_index = True
    
    token: Mapped[str] = mapped_column(String, nullable=False)
    type_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)