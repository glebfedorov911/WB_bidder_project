from pydantic import BaseModel, field_validator, ValidationError, model_validator

from enum import Enum
from typing import Self
from datetime import datetime

from utils.exceptions import *
from .settings import settings


class ModeBidder(Enum):
    DEFAULT = "default"
    MOMENTUM = "momentum"
    NEURO = "neuro"

class TypeCampaign(Enum):
    AUTOMATIC = "automatic"
    AUCTION = "auction"

    def __new__(cls, code: str):
        obj = object.__new__(cls)
        obj._value_ = code
        return obj

    @property
    def wb_code(self) -> int:
        wb_status = {
            TypeCampaign.AUTOMATIC: 8,
            TypeCampaign.AUCTION: 9,
        }
        if not (status := wb_status.get(self, None)):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return status

class BidderAndCPMSchemaMixin(BaseModel):
    advertId: int
    type: TypeCampaign

    @field_validator("type", mode="before")
    @classmethod
    def convert_enum_to_value(cls, value: str) -> TypeCampaign:
        try:
            return TypeCampaign(value)
        except:
            raise ValueError(INVALID_DATA_FOR_TYPE_CAMPAIGN.format(value=value))

class BidderData(BidderAndCPMSchemaMixin):
    max_cpm_campaign: int
    min_cpm_campaign: int = settings.cpm_var.min_cpm
    wish_place_in_top: int
    type_work_bidder: ModeBidder = ModeBidder.DEFAULT
    step: int = settings.cpm_var.step_cpm

    @model_validator(mode="after")
    def check_max_relative_min(self) -> Self:
        if self.max_cpm_campaign < self.min_cpm_campaign:
            raise ValueError(MIN_GREATHER_THEN_MAX)
        return self

    @field_validator("min_cpm_campaign", "max_cpm_campaign", mode="before")
    @classmethod
    def check_valid_campaign(cls, value: int) -> int:
        cpm_default = settings.cpm_var.min_cpm

        if value < cpm_default:
            return cpm_default
        return value

class CPMChangeSchema(BidderAndCPMSchemaMixin):
    cpm: int
    param: int = None
    instrument: int = None

class PeriodTime(BaseModel):
    start: datetime
    end: datetime

    @field_validator("start", "end", mode="before")
    def check_valid_data(self, value):
        splited_date = str(value).split("-")
        year, month, day = list(map(str, splited_date))
        
        if self._check_valid_data_format(date=splited_date):
            raise ValueError(INVALID_DATA_FORMAT)
        
        if self._check_valid_year_format(year=year):
            raise ValueError(INVALID_YEAR_FORMAT)
        
        if self._check_valid_month_format(month=month):
            raise ValueError(INVALID_MONTH_FORMAT)
        
        if self._check_valid_day_format(day=day):
            raise ValueError(INVALID_DAY_FORMAT)

        return datetime(value).strftime("%Y-%m-%d")

    def _check_valid_data_format(self, date: str):
        return len(split_data) < 3
        
    def _check_valid_year_format(self, year: str):
        return 4 <= len(year) < 5

    def _check_valid_month_format(self, month):
        return 2 <= len(month) < 3

    def _check_valid_day_format(self, day):
        return 2 <= len(day) < 3

class OrderBy(BaseModel):
    field: str = "avgPosition"
    mode: str = "asc"

class CurrentPositionSchema:
    currentPeriod: PeriodTime
    pastPeriod: PeriodTime
    nmIds: list
    topOrderBy: str = "openCard"
    orderBy: OrderBy
    limit: int

    @field_validator("limit", mode="before")
    @classmethod
    def check_valid_limit(cls, value):
        if 0 < value <= 30:
            return value
        raise ValueError(INVALID_LIMIT_VALUE)