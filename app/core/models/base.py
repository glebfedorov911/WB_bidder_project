from sqlalchemy.orm import declared_attr, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

import uuid


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),\
        primary_key=True, default=uuid.uuid4)