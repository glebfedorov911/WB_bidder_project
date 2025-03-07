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