from .schemas import BidderData, CPMChangeSchema, TypeCampaign
from .exception import *
from .settings import *

import httpx

from abc import ABC, abstractmethod


class Calculator(ABC):

    @abstractmethod
    def calculate_start_cpm(self) -> int:
        ...

class CalculatorCPM(Calculator):

    def __init__(self, min_cpm: int, max_cpm: int):
        self.min_cpm = min_cpm
        self.max_cpm = max_cpm

    def calculate_start_cpm(self) -> int:
        part_max_cpm = self.max_cpm // 3

        return part_max_cpm if self._check_valid_cpm(part_max_cpm=part_max_cpm) else self.min_cpm

    def _check_valid_cpm(self, part_max_cpm: int) -> bool:
        return part_max_cpm > self.min_cpm

class ManagerCPM:

    def increase_cpm(self, cpm: int, step: int) -> int:
        return cpm + step

class Bidder:
    def __init__(self, bidder_data: BidderData, cpm_change: CPMChangeSchema, cpm_manager: ManagerCPM, calculator: Calculator):
        super().__init__()
        
        self.max_cpm_campaign = bidder_data.max_cpm_campaign
        self.min_cpm_campaign = bidder_data.min_cpm_campaign
        self.wish_place_in_top = bidder_data.wish_place_in_top
        self.type_work_bidder = bidder_data.type_work_bidder
        self.step = bidder_data.step

        self.advertId = cpm_change.bidder_data
        self.type = self._get_wb_code_for_type(type_campaign=cpm_change.type)
        self.cpm = cpm_change.cpm
        self.param = cpm_change.param
        self.instrument = cpm_change.instrument

        self.calculator = calculator
        self.cpm_manager = cpm_manager

        self.start_cpm = self._get_start_cpm_campaign()
        
    def _get_wb_code_for_type(self, type_campaign: TypeCampaign) -> int:
        if not hasattr(type_campaign, "wb_code"):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return type_campaign.wb_code

    def _get_start_cpm_campaign(self) -> int:
        return self.calculator.calculate_start_cpm()

#TODO: Написать работу с вб, ТЕСТЫ!!!