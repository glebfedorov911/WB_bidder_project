from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os


class SettingsCPM(BaseModel):
    step_cpm: int = 2
    min_cpm: int = 100
    default_dif_between_position_momentum_mode: int = 10

class SettingsParser(BaseModel):
    url_to_plugin: str = os.path.expanduser(
    "~/Library/Application Support/Google/Chrome/Default/Extensions/eabmbhjdihhkdkkmadkeoggelbafdcdd/2.15.5_0"
    )


class Settings(BaseSettings):
    cpm_var: SettingsCPM = SettingsCPM()

settings = Settings()