from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
import os

from dotenv import load_dotenv

from .schemas import (
    BidderData, CurrentPositionSchema, OrderBy, PeriodTime,
    ModeBidder, CPMChangeSchema
)
from .manager_cpm import ManagerCPMFabric, ManagerCPMRegistry
from .calculator_cpm import CalculatorCPMFabric, CalculatorCPMRegisty
from .wildberries_api import (
    WBApiFabric, WBApiRegistry, 
    WildberriesBidderStatsWorker, WildberriesBidderCPMWorker   
)
from .settings import settings
from utils.http_client import BaseHttpClient, HttpxHttpClient


class Bidder(ABC):


    @abstractmethod
    async def start(self): ...

class DefaultBidder:


    def __init__(
        self,
        bidder_data: BidderData, 
        http_client: BaseHttpClient,
        token: str,
        articuls: list
    ):  
        self.bidder_data = bidder_data
        self.calculator = CalculatorCPMFabric.create_obj(
            self.bidder_data.type_work_bidder, CalculatorCPMRegisty,
            min_cpm=self.bidder_data.min_cpm_campaign,
            max_cpm=self.bidder_data.max_cpm_campaign 
        )
        self.cpm_handler = WBApiFabric.create_obj(
            'cpm', WBApiRegistry,
            token=token,
            http_client=http_client
        )
        self.stats_handler: WildberriesBidderStatsWorker = WBApiFabric.create_obj(
            "stats", WBApiRegistry,
            token=token,
            http_client=http_client
        )
        self.articuls = articuls

    async def start(self):
        current_position = await self._get_current_position()
        print("Текущая позиция: ", current_position)
        if current_position == self.bidder_data.wish_place_in_top:
            print("Закончили")
            return True
        if self.calculator.min_cpm >= self.calculator.max_cpm:
            print("Закончили, ставка превысила ожидание")
            return True

        manager = self._create_manager_cpm(
            current_position=current_position
        )
        current_cpm = manager.increase_cpm()
        await self._change_cpm(current_cpm)
        print("Изменили ставку до", current_cpm)

    def _create_manager_cpm(
        self, current_position
    ):
        return ManagerCPMFabric.create_obj(
            self.bidder_data.type_work_bidder, ManagerCPMRegistry,
            cpm=self.calculator.calculate_start_cpm(),
            step=self.bidder_data.step,
            current_position=current_position,
            wish_position=self.bidder_data.wish_place_in_top
        )

    async def _get_current_position(self):
        today = self._get_today_date_with_ymd_format()
        schema = CurrentPositionSchema(
            currentPeriod=PeriodTime(
                start=today,
                end=today
            ),
            nmIds=self.articuls,
            orderBy=OrderBy()
        )
        stats = await self.stats_handler.run(schema)

        return self._get_current_position_from_stats(stats)

    @staticmethod
    def _get_today_date_with_ymd_format():
        return datetime.today().strftime("%Y-%m-%d")

    @staticmethod
    def _get_current_position_from_stats(stats: dict):
        return stats['data']['groups'][0]['items'][0]['avgPosition']['current']
    
    async def _change_cpm(self, cpm: int):
        schema = CPMChangeSchema(
            advertId=self.bidder_data.advertId,
            cpm=cpm
        )
        await self.cpm_handler.run(schema)
        self.calculator.min_cpm = cpm

load_dotenv()

TOKEN = os.getenv("API_TOKEN")
bidder_data = BidderData(
    advertId=23636560,
    max_cpm_campaign=350,
    min_cpm_campaign=203,
    wish_place_in_top=32,
    type_work_bidder=ModeBidder.DEFAULT,
    step=settings.cpm_var.step_cpm
)
http_client = HttpxHttpClient()
articuls = [240664574]

bidder = DefaultBidder(
    bidder_data=bidder_data,
    http_client=http_client,
    token=TOKEN,
    articuls=articuls
)

import time
for _ in range(10):
    try:
        def m():
            return asyncio.run(bidder.start())

        r = m()
        if r:
            print("стоп")
            break

    except Exception as e:
        print(e)
    time.sleep(120)