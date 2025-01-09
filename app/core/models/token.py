from .base import Base

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

import uuid 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Token(Base):
    token: Mapped[str] = mapped_column(String, nullable=False)
    type_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), \
        ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tokens")