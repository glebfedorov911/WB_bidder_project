from pydantic_settings import BaseSettings
from pydantic import BaseModel

from .config import URL, ECHO


class DataBaseSetting(BaseModel):
    url: str = URL
    echo: bool = ECHO

class API(BaseModel):
    prefix: str = "/api"
    v0: str = "/v0"

class Settings(BaseSettings):
    db_settings: DataBaseSetting = DataBaseSetting()
    api: API = API()

settings: Settings = Settings()