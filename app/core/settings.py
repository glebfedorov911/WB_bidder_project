from pydantic_settings import BaseSettings
from pydantic import BaseModel

from .config import URL, ECHO


class DataBaseSetting(BaseModel):
    url: str = URL
    echo: bool = ECHO

class Settings(BaseSettings):
    db_settings: DataBaseSetting = DataBaseSetting()

settings: Settings = Settings()