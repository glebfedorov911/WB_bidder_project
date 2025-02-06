from pydantic import BaseModel
from pydantic_settings import BaseSettings


class SettingsCPM(BaseModel):
    step_cpm: int = 2
    min_cpm: int = 100
    default_dif_between_position_momentum_mode: int = 10

class Settings(BaseSettings):
    cpm_var: SettingsCPM = SettingsCPM()

settings = Settings()