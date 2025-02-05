from .schemas import BidderData, CPMChangeSchema, TypeCampaign
from .exception import *
from .settings import *

import httpx

from abc import ABC, abstractmethod


class CalculatorCPM(ABC):

    @abstractmethod
    def calculate_start_cpm(self) -> int:
        ...

class StandardCalculatorCPM(CalculatorCPM):

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
    def __init__(self, bidder_data: BidderData, cpm_change: CPMChangeSchema, cpm_manager: ManagerCPM, calculator: CalculatorCPM):
        super().__init__()
        
        self.bidder_data = bidder_data
        self.cpm_change = cpm_change

        self.calculator = calculator
        self.cpm_manager = cpm_manager

        self.type_campaign = self._get_wb_code_for_type(type_campaign=self.cpm_change.type) 
        self.start_cpm = self._get_start_cpm_campaign()
        
    def _get_wb_code_for_type(self, type_campaign: TypeCampaign) -> int:
        if not hasattr(type_campaign, "wb_code"):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return type_campaign.wb_code

    def _get_start_cpm_campaign(self) -> int:
        return self.calculator.calculate_start_cpm()

#TODO: Написать работу с вб, ТЕСТЫ!!!
#TODO: ПЕРЕДАВАТЬ РЕЖИМ В ФАБРИКУ И ТАМ ЧЕКАТЬ КАКОЙ РЕЖИМ РАБОТЫ