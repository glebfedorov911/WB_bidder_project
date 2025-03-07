from utils.exceptions import *
from utils.http_client import BaseHttpClient, HttpxHttpClient
from .schemas import (
    BidderData, CPMChangeSchema, TypeCampaign, CurrentPositionSchema,
    ModeBidder, PeriodTime, OrderBy
)
from .settings import *

from pydantic import BaseModel
import httpx
import datetime
import asyncio
import json

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
    def increase_cpm(self, cpm: int, step: int) -> int:
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
    def __init__(self, api: str, url: str, http_client: BaseHttpClient):
        self.api = api 
        self.http_client = http_client
        self.url = url

    def _get_data_for_request(self, data_to_request: BaseModel) -> dict:
        result = data_to_request.model_dump()
        for i in result.copy():
            if result[i] is None:
                del result[i]
        return json.dumps(result)
    
    async def _send_request_and_get_json_from_response(self, method: str, data_to_request: dict) -> dict:
        response = await self.http_client.send_request(
            method=method,
            url=self.url,
            data=data_to_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": self.api
            }
        )

        return self._get_json_from_response(response=response)
    
    def _get_json_from_response(self, response: httpx.Response) -> dict:
        return response.json()

class WildberriesBidderCPMWorker(WildberriesBidderWorkerMixin):
    def __init__(self, api: str, url: str, http_client: BaseHttpClient):
        super().__init__(url=url, api=api, http_client=http_client)

    async def change_cpm(self, change_cpm: CPMChangeSchema) -> dict:
        change_cpm_for_request = self._get_data_for_request(data_to_request=change_cpm)

        return await self._send_request_and_get_json_from_response(method="post", data_to_request=change_cpm_for_request)

class WildberriesBidderStatsWorker(WildberriesBidderWorkerMixin):
    def __init__(self, api: str, url: str, http_client: BaseHttpClient):
        super().__init__(url=url, api=api, http_client=http_client)

    async def get_current_position_in_top(self, current_position_form: CurrentPositionSchema):
        current_position_form_for_request = self._get_data_for_request(data_to_request=current_position_form)
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=current_position_form_for_request)


class DefaultBidder:
    def __init__(
        self, 
        bidder_data: BidderData, 
        cpm_manager: ManagerCPM, 
        calculator: CalculatorCPM,
        cpm_worker: WildberriesBidderCPMWorker,
        stats_worker: WildberriesBidderStatsWorker,
    ):
        super().__init__()
        
        self.bidder_data = bidder_data

        self.calculator = calculator
        self.cpm_manager = cpm_manager

        self.type_campaign_wb_style = self._get_wb_code_for_type(type_campaign=self.bidder_data.type) 
        self.start_cpm = self._get_start_cpm_campaign()
        self.stats_worker = stats_worker
        self.cpm_worker = cpm_worker


    def _get_wb_code_for_type(self, type_campaign: TypeCampaign) -> int:
        if not hasattr(type_campaign, "wb_code"):
            raise ValueError(INVALID_CAMPAIGN_TYPE_WB_CODE_MISSING)
        return type_campaign.wb_code

    def _get_start_cpm_campaign(self) -> int:
        return self.calculator.calculate_start_cpm()

    async def bidder(self):
        current_position = CurrentPositionSchema(
            currentPeriod = PeriodTime(
                start='2025-03-07',
                end='2025-03-07',
            ),
            nmIds=[240664574],
            orderBy=OrderBy(),
            limit=1,
        )
        current_position = await self.stats_worker.get_current_position_in_top(current_position_form=current_position)
        print(current_position)

class MomentumBidder:
    ...

class NeuroBidder:
    ...


if __name__ == "__main__":
    bidder_data = BidderData(
        max_cpm_campaign=350,
        min_cpm_campaign=155,
        wish_place_in_top=17,
        type_work_bidder=ModeBidder.DEFAULT,
        advertId=23636560,
        type=TypeCampaign.AUTOMATIC 
    )

    cpm_manager = DefaultManagerCPM()
    calculator = StandardCalculatorCPM(
        bidder_data.min_cpm_campaign,
        bidder_data.max_cpm_campaign
    )
    http_client = HttpxHttpClient()
    token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzEyMzM2OSwiaWQiOiIwMTk1NzBkZS00MzA3LTdiOWMtODM4Yi1kMjIyYmQ2OGQwOGUiLCJpaWQiOjI5MzgxMTkzLCJvaWQiOjE4Mjk2NywicyI6MTI2LCJzaWQiOiJjZTYzZjU4YS05ODI3LTRiMzctOTQ1YS1iMTNlNWQ4NmZjZTUiLCJ0IjpmYWxzZSwidWlkIjoyOTM4MTE5M30.SlFB07pm17jIP7AumxQ4MqWA0o6ULrjE4uWN00Fm5b6AHebM_8pQw9TZ5RH-b5tjjT8Fp8Od3Gt2nIeo2E9R-A"
    stats = WildberriesBidderStatsWorker(api=token, url="https://seller-analytics-api.wildberries.ru/api/v2/search-report/product/search-texts", http_client=http_client)
    cpm = WildberriesBidderCPMWorker(api=token, http_client=http_client, url="https://advert-api.wildberries.ru/adv/v0/cpm")

    bidder = DefaultBidder(
        bidder_data=bidder_data,
        cpm_manager=cpm_manager, 
        calculator=calculator,
        cpm_worker=cpm,
        stats_worker=stats
    )

    def main():
        asyncio.run(bidder.bidder())
    main()