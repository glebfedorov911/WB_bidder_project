from abc import ABC, abstractmethod
import json

from pydantic import BaseModel
import httpx

from utils.http_client import HttpxHttpClient, BaseHttpClient
from .custom_exceptions import WBException
from .schemas import (
    CurrentPositionSchema, PeriodTime, OrderBy,
    CPMChangeSchema
)
from .utils import BaseFabric, BaseRegistry


URL_CPM = "https://advert-api.wildberries.ru/adv/v0/cpm"
URL_STAT = "https://seller-analytics-api.wildberries.ru/api/v2/search-report/report"

class DataConverter:
    
    @classmethod
    def get_clear_data(self, data: BaseModel):
        data_dict = data.model_dump()
        for i in list(data_dict.keys()):
            if data_dict[i] is None:
                del data_dict[i]
        return json.dumps(data_dict)

class WildberriesBidderWorkerMixin:
    def __init__(self, token: str, url: str, http_client: BaseHttpClient):
        self.token = token 
        self.http_client = http_client
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
    
    async def _send_request_and_get_json_from_response(self, method: str, data_to_request: BaseModel) -> dict:
        response = await self.http_client.send_request(
            method=method,
            url=self.url,
            data=self._get_data_for_request(data_to_request),
            headers=self.headers
        )

        return self._get_json_from_response(response=response)
    
    def _get_data_for_request(self, data_to_request: BaseModel) -> dict:
        return DataConverter.get_clear_data(data_to_request)
        
    def _get_json_from_response(self, response: httpx.Response) -> dict:
        if response.status_code != 200:
            raise ValueError(WBException.INVALID_REQUEST)
        try:
            return response.json()
        except json.JSONDecodeError:
            ...
        return {}
        
class WBApi(ABC):

    
    @abstractmethod
    async def run(schema: BaseModel) -> dict: ...

class WildberriesBidderCPMWorker(WBApi, WildberriesBidderWorkerMixin):
    def __init__(self, token: str, http_client: BaseHttpClient):
        super().__init__(url=URL_CPM, token=token, http_client=http_client)

    async def run(self, schema: CPMChangeSchema) -> dict:
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=schema)

class WildberriesBidderStatsWorker(WBApi, WildberriesBidderWorkerMixin):
    def __init__(self, token: str, http_client: BaseHttpClient):
        super().__init__(url=URL_STAT, token=token, http_client=http_client)

    async def run(self, schema: CurrentPositionSchema):
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=schema)


class WBApiRegistry(BaseRegistry): 
    _registry = {}

class WBApiFabric(BaseFabric): ...

WBApiRegistry.register_obj("stats", WildberriesBidderStatsWorker)
WBApiRegistry.register_obj("cpm", WildberriesBidderCPMWorker)