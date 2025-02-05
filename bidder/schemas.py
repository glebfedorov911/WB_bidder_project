from pydantic import BaseModel, field_validator, ValidationError

from enum import Enum

from .exception import *


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

class BidderData(BaseModel):
    good_articul: str
    max_sum_good: int
    min_sum_good: int
    wish_place_in_top: int
    type_work_bidder: ModeBidder

class CPMChangeSchema(BaseModel):
    advertId: int
    type: TypeCampaign
    cpm: int
    param: int = None
    instrument: int = None

    @field_validator("type", mode="before")
    @classmethod
    def convert_enum_to_value(cls, value: str) -> TypeCampaign:
        try:
            return TypeCampaign(value)
        except:
            raise ValueError(INVALID_DATA_FOR_TYPE_CAMPAIGN.format(value=value))