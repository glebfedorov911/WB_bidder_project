from pydantic import BaseModel, Field, model_validator

import httpx
import asyncio
import enum
import os

from dotenv import load_dotenv


load_dotenv()

# TODO: ВЫНЕСТИ В ОТДЕЛЬНЫЕ КЛАССЫ
# Валидация данных (например, time_fast_mode_validation). -> HTTP-клиент для работы с API. APIClient
# Работа с HTTP (make_request_to_change_price, show_status). -> Логика валидации вынесена в отдельные классы или функции. Validator
# Логика расчета и изменения цены (edit_price_by_position, algorithm_step_price_fast_mode и др.). -> Управление процессами изменения ставки в отдельном классе. BidManager
# ЭТО ПРИНЦИПЫ SOLID

# TODO: ДОПИСАТЬ ДАЛЬНЕЙШИЙ ФУНКЦИОНАЛ

# TODO: ИСПОЛЬЗОВАТЬ REDIS ДЛЯ СОХРАНЕНИЯ ДАННЫХ О СТАВКАХ И ТД, ПОСЛЕ ОКОНЧАНИЯ РАБОТЫ СОХРАНЯТЬ В ОБЫЧНУЮ БД

class StatusTarget(enum.Enum):
    STAY_BID = "Удерживать ставку"
    # TODO: Здесь доработать еще статуы

class SettingParamsFastMode(BaseModel):
    use_fast_mode: bool
    time_fast_mode: int = Field(ge=0)

class ParamsStandartBid(BaseModel):
    CPM: int = Field(ge=1)
    max_bid: int = Field(ge=1)
    wish_position: int = Field(ge=1)
    target: StatusTarget
    step_bid: int = Field(ge=1)

    @model_validator(mode="before")
    def check_step_bid(cls, values):
        CPM = values.get("CPM")
        step_bid = values.get("step_bid")
        if step_bid > CPM:
            raise ValueError("Bad value, stepBid cannot be greater then CPM")
        return values

class CampaignBig(BaseModel):
    MIN_LENGTH_TYPE: int = 4
    MAX_LENGTH_TYPE: int = 9

    advert_id: int
    type: int = Field(ge=MIN_LENGTH_TYPE, le=MAX_LENGTH_TYPE)
    param: int #я хз чо тут указывать, пока что не понял

class ResponseChangeCPM(CampaignBig):
    CPM_price: int

class AutoBidder:
    INTERVAL_BETWEEN_RESPONSE = 600000 # 10 минут
    INTERVAL_BETWEEN_RESPONSE_FAST_MODE = 60000 # минута
    def __init__(self, campaign_info: CampaignBig, standart_bid: ParamsStandartBid, fast_mode: SettingParamsFastMode):
        self.CPM = standart_bid.CPM
        self.current_CPM = self.CPM // 2
        self.max_bid = standart_bid.max_bid
        self.wish_position = standart_bid.wish_position
        self.target = standart_bid.target
        self.step_bid = standart_bid.step_bid
        self.use_fast_mode = fast_mode.use_fast_mode
        self.time_fast_mode = self.time_fast_mode_validation(fast_mode.time_fast_mode)
        self.headers = self.create_headers()
        self.advert_id = campaign_info.advertId
        self.type = campaign_info.type
        self.param = campaign_info.param

    def time_fast_mode_validation(self, time_fast_mode):
        if time_fast_mode < 60_000:
            raise ValueError("Not Valid time_fast_mode. Need greater then 60 seconds")
        return time_fast_mode

    @staticmethod
    def create_headers():
        TOKEN = os.getenv("TOKEN")
        return  {   "Authorization": TOKEN    }

    async def change_price(self, current_position: int) -> None: #current_position получать из запроса
        if self.should_skip_price_change():
            return
        self.edit_price_by_position(current_position)

        url_for_change_price = "https://discounts-prices-api.wildberries.ru/api/v2/upload/task"
        response_body = self.valid_body_to_change_CPM()
        self.validation_change_price(url_for_change_price, response_body)
        await self.sleeping_between_change_price()

    def should_skip_price_change(self, current_position) -> None:
        return current_position == self.wish_position or self.time_fast_mode <= self.INTERVAL_BETWEEN_RESPONSE_FAST_MODE

    def edit_price_by_position(self, current_position: int) -> None:
        self.adjust_current_CPM(current_position)
        self.lower_remainder_time_fast_mode()

    def adjust_current_CPM(self, current_position) -> None:
        changerPrice = self.algorithm_step_price_fast_mode() if self.use_fast_mode else self.step_bid
        self.current_CPM += changerPrice if current_position > self.wish_position else -changerPrice

    def algorithm_step_price_fast_mode(self) -> int:
        TIME_UPPER = 4
        differenceBid = self.CPM - self.currentCPM
        return differenceBid // (self.time_fast_mode * TIME_UPPER)

    def lower_remainder_time_fast_mode(self) -> None:
        if self.use_fast_mode and self.time_fast_mode > self.INTERVAL_BETWEEN_RESPONSE_FAST_MODE:
            self.time_fast_mode -= self.INTERVAL_BETWEEN_RESPONSE_FAST_MODE

    def valid_body_to_change_CPM(self) -> ResponseChangeCPM:
        return ResponseChangeCPM(advertId=self.advert_id, type=self.type, cpm=self.current_CPM, param=self.param)

    async def validation_change_price(self, url: str, body: ResponseChangeCPM) -> None:
        try:
            await self.make_request_to_change_price(url, body)
        except Exception as e:
            print(f"Некорректные данные | {e}")

    async def make_request_to_change_price(self, url: str, body: ResponseChangeCPM):
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body.dict())
            self.show_status(response=response)
    
    def show_status(self, response: httpx.AsyncClient):
        status = "Цена успешно изменена" if response.status_code == 200 else "Цена не изменена"
        print(status)

    async def sleeping_between_change_price(self):
        interval = self.INTERVAL_BETWEEN_RESPONSE_FAST_MODE if self.use_fast_mode else self.INTERVAL_BETWEEN_RESPONSE
        await asyncio.sleep(interval)