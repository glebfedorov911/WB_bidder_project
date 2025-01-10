from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import String, Enum as SQLEnum, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .mixin import DateMixin
from .types.emailtype import EmailType
from .enum.accountstatus import AccountStatus
from .enum.accountrole import AccountRole
from .enum.subscriptionstatus import SubscriptionStatus
from core.settings import settings


if TYPE_CHECKING:
    from .token import Token
    from .verification_codes import VerificationCode


class User(DateMixin, Base):
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    email: Mapped[EmailType] = mapped_column(EmailType, nullable=True, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    account_status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus), 
        nullable=False,
        default=AccountStatus.PENDING, 
        index=True
    )
    account_role: Mapped[AccountRole] = mapped_column(
        SQLEnum(AccountRole), 
        nullable=False,
        default=AccountRole.DEFAULT_USER,
        index=True
    )
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    has_subscription: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True
    )
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus), 
        nullable=False,
        default=SubscriptionStatus.STANDARD, 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )
    subscription_active_until: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, index=True
    )

    tokens = relationship("Token", back_populates="user")
    code = relationship("VerificationCode", back_populates="user")

    @property
    def fullname(self) -> str:
        parts_name = [self.lastname, self.firstname] 
        if self.patronymic:
            parts_name.append(self.patronymic)
        return " ".join(parts_name).strip()

    def set_subcription_end(self):
        SUBSCRIPTION_END = 1
        if self.subscription_status == SubscriptionStatus.STANDARD:
            self.subscription_active_until = datetime.utcnow() + timedelta(days=settings.subscription.STANDARD_EXPIRE_DAYS)
        else:
            self.subscription_active_until = datetime.utcnow() - timedelta(days=SUBSCRIPTION_END)