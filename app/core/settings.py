from pydantic_settings import BaseSettings
from pydantic import BaseModel
import logging

from .config import (
    URL, ECHO, SECRET_KEY, SMSC_LOGIN, SMSC_PSW, SMSC_TG, SMSC_URL
)
from .logger import StatBerryLogger


class DataBaseSetting(BaseModel):
    url: str = URL
    echo: bool = ECHO

class API(BaseModel):
    prefix: str = "/api"
    v0: str = "/v0"

class Auth(BaseModel):
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 1800
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604_800
    TOKEN_TYPE: str = "Bearer"
    PASSWORD_LENGTH: int = 8

class Subscription(BaseModel):
    STANDARD_EXPIRE_DAYS: int = 1

class SMSC(BaseModel):
    SMSC_LOGIN: str = SMSC_LOGIN
    SMSC_PSW: str = SMSC_PSW
    SMSC_TG: str = SMSC_TG
    SMSC_URL: str = SMSC_URL

class Settings(BaseSettings):
    db_settings: DataBaseSetting = DataBaseSetting()
    api: API = API()
    auth: Auth = Auth()
    subscription: Subscription = Subscription()
    smsc: SMSC = SMSC()
    statberry_logger: StatBerryLogger = StatBerryLogger(loggername="StatBerry", filename="statberry.log")


settings: Settings = Settings()