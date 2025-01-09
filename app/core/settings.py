from pydantic_settings import BaseSettings
from pydantic import BaseModel

from .config import URL, ECHO, SECRET_KEY


class DataBaseSetting(BaseModel):
    url: str = URL
    echo: bool = ECHO

class API(BaseModel):
    prefix: str = "/api"
    v0: str = "/v0"

class Auth(BaseModel):
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

class Settings(BaseSettings):
    db_settings: DataBaseSetting = DataBaseSetting()
    api: API = API()
    auth: Auth = Auth()

settings: Settings = Settings()