from utils.exceptions import *
from utils.http_client import BaseHttpClient, HttpxHttpClient
from .schemas import BidderData, CPMChangeSchema, TypeCampaign, CurrentPositionSchema
from .settings import *

from pydantic import BaseModel
import httpx
import asyncio

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

class ManagerCPM(ABC):
    
    @abstractmethod
    def change_cpm(self, cpm: int, step: int) -> int:
        ...

class DefaultManagerCPM(ManagerCPM):

    def increase_cpm(self, cpm: int, step: int) -> int:
        return cpm + step

class MomentumManagerCPM(ManagerCPM):
    DEFAULT_DIF_PLACES = settings.cpm_var.default_dif_between_position_momentum_mode
    MINIMUM_STEP = settings.cpm_var.step_cpm

    def __init__(self, current_position: int, wish_position: int):
        self.current_position = current_position
        self.wish_position = wish_position

    def set_new_current_position(self, new_position) -> None:
        self.current_position = new_position

    def increase_cpm(self, cpm: int, step: int) -> int:
        use_minimum_step = self._check_dif_between_positions() 
        return cpm + (self.MINIMUM_STEP if use_minimum_step else step)

    def _check_dif_between_positions(self):
        return abs(self.wish_position - self.current_position) < self.DEFAULT_DIF_PLACES 

class WildberriesBidderWorkerMixin:
    def __init__(self, url: str, http_client: BaseHttpClient):
        self.http_client = http_client
        self.url = url

    def _get_data_for_request(self, data_to_request: BaseModel) -> dict:
        return data_to_request.model_dump()
    
    async def _send_request_and_get_json_from_response(self, method: str, data_to_request: dict) -> dict:
        response = await self.http_client.send_request(
            method=method,
            url=self.url,
            json=data_to_request
        )

        return self._get_json_from_response(response=response)
    
    def _get_json_from_response(self, response: httpx.Response) -> dict:
        return response.json()

class WildberriesBidderCPMWorker(WildberriesBidderWorkerMixin):
    def __init__(self, url: str, http_client: BaseHttpClient):
        super().__init__(url=url, http_client=http_client)

    async def change_cpm(self, change_cpm: CPMChangeSchema) -> dict:
        change_cpm_for_request = self._get_data_for_request(change_cpm=change_cpm)

        return await self._send_request_and_get_json_from_response(method="post", change_cpm_for_request=change_cpm_for_request)

class WildberriesBidderStatsWorker(WildberriesBidderWorkerMixin):
    def __init__(self, url: str, http_client: BaseHttpClient):
        super().__init__(url=url, http_client=http_client)

    async def get_current_position_in_top(self, current_position_form: CurrentPositionSchema):
        current_position_form_for_request = self._get_data_for_request(data_to_request=current_position_form)
        
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=current_position_form_for_request)

class Bidder:
    
    def __init__(self, bidder_data: BidderData, cpm_manager: ManagerCPM, calculator: CalculatorCPM):
        super().__init__()
        
        self.bidder_data = bidder_data

        self.calculator = calculator
        self.cpm_manager = cpm_manager

        self.type_campaign_wb_style = self._get_wb_code_for_type(type_campaign=self.bidder_data.type) 
        self.start_cpm = self._get_start_cpm_campaign()
        
    def _get_wb_code_for_type(self, type_campaign: TypeCampaign) -> int:
        if not hasattr(type_campaign, "wb_code"):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return type_campaign.wb_code

    def _get_start_cpm_campaign(self) -> int:
        return self.calculator.calculate_start_cpm()

class DefaultBidder(Bidder):
    ...

class MomentumBidder(Bidder):
    ...

class NeuroBidder(Bidder):
    ...

#TODO: ТЕСТЫ!!!
#TODO: ПЕРЕДАВАТЬ РЕЖИМ В ФАБРИКУ И ТАМ ЧЕКАТЬ КАКОЙ РЕЖИМ РАБОТЫ