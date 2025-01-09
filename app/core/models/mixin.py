from typing import TYPE_CHECKING
from datetime import datetime
import uuid 

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from .user import User


class VerificationCodeAndTokenMixin:
    _back_populates: str = None 
    _user_id_nullable: bool = False   

    @declared_attr
    def user_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id"), 
            nullable=cls._user_id_nullable
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(
            "User",
            back_populates=cls._back_populates
        )

class DateMixin:
    _created_at_nullable: bool = False

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime, 
            nullable=cls._created_at_nullable,
            default=datetime.utcnow
        )