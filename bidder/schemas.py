from pydantic import BaseModel, field_validator, ValidationError, model_validator, model_serializer

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
    type: TypeCampaign = TypeCampaign.AUTOMATIC.wb_code

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
    start: str
    end: str

    @field_validator("start", "end", mode="before")
    @classmethod
    def check_valid_data(cls, value):
        splited_date = str(value).split("-")
        year, month, day = list(map(str, splited_date))
        
        if len(splited_date) < 3:
            raise ValueError(INVALID_DATA_FORMAT)
        
        if not (4 <= len(year) < 5):
            raise ValueError(INVALID_YEAR_FORMAT)
        
        if not (2 <= len(month) < 3):
            raise ValueError(INVALID_MONTH_FORMAT)
        
        if not(2 <= len(day) < 3):
            raise ValueError(INVALID_DAY_FORMAT)

        return value

class OrderBy(BaseModel):
    field: str = "avgPosition"
    mode: str = "asc"

class CurrentPositionSchema(BaseModel):
    currentPeriod: PeriodTime
    pastPeriod: PeriodTime | None = None
    nmIds: list
    subjectIds: list | None = None
    brandNames: list | None = None
    tagIds: list | None = None
    positionCluster: str = "all"
    orderBy: OrderBy
    limit: int = 100
    offset: int = 0

    @field_validator("limit", mode="before")
    @classmethod
    def check_valid_limit(cls, value):
        if 0 < value <= 1000:
            return value
        raise ValueError(INVALID_LIMIT_VALUE)

class AuthPluginSchema(BaseModel):
    login: str
    password: str

class AuthPluginSelectors(BaseModel):
    login_button: str = ".button-link.qa-product-widget-button-go-to-analytics"
    login_field_auth: str = ".authorization-input"
    password_field_auth: str = ".authorization-input.qa-password"
    auth_button: str = ".btn.btn-md.btn-secondary.authorization-button.qa-button-login"
    good_auth: str = "#mmodalpublic___BV_modal_title_"

class WbSelectors(BaseModel):
    next_page: str = ".pagination-next.pagination__next.j-next-page"

    can_parse_data: str = ".cpm-card-widget.eggheads-bootstrap"
    goods_on_page: str = ".cpm-card-widget.eggheads-bootstrap"
    wb_articul: str = "id"
    marks: str = "#{articul_wb} > div.product-card__wrapper > div.product-card__bottom-wrap > p.product-card__rating-wrap > span.address-rate-mini.address-rate-mini--sm"
    count_marks: str = "#{articul_wb} > div.product-card__wrapper > div.product-card__bottom-wrap > p.product-card__rating-wrap > span.product-card__count"
    fbo: str = "#{articul_wb} > div.product-card__wrapper > div.list-widget.eggheads-product-list-widget.eggheads-bootstrap > div.b-overlay-wrap.position-relative.eggheads-overlay > ul > li:nth-child(2) > span.text.-bold"
    num_of_the_rating: str = "#{articul_wb} > div.product-card__wrapper > div.list-widget.eggheads-product-list-widget.eggheads-bootstrap > div.list-widget__number"
    from_value: str = "div > div > span > span"
    price: str = ".title"