from .base import Base
from .types.emailtype import EmailType
from .enum.accountstatus import AccountStatus
from .enum.accountrole import AccountRole
from .enum.subscriptionstatus import SubscriptionStatus

from datetime import datetime

from sqlalchemy import String, Enum as SQLEnum, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .token import Token


class User(Base):
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(EmailType, nullable=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    account_status: Mapped[AccountStatus] = mapped_column(SQLEnum(AccountStatus), \
        nullable=False, default=AccountStatus.PENDING)
    account_role: Mapped[AccountRole] = mapped_column(SQLEnum(AccountRole), \
        nullable=False, default=AccountRole.DEFAULT_USER)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    has_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(\
        SQLEnum(SubscriptionStatus), \
        nullable=False, default=SubscriptionStatus.STANDARD)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, \
        default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    subscription_active_until: Mapped[datetime] = mapped_column(DateTime, \
        nullable=True)

    tokens = relationship("Token", back_populates="user")