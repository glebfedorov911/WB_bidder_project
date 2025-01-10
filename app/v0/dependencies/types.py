from typing import TypeVar

from pydantic import BaseModel

from core.models.token import Base
from .builders import QueryBuilder


schema_type = TypeVar("S", bound=BaseModel) 
model_type = TypeVar("M", bound=Base)
builder_type = TypeVar("B", bound=QueryBuilder) 