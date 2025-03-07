from pydantic import BaseModel


URL_CPM = "https://advert-api.wildberries.ru/adv/v0/cpm"
URL_STAT = "https://seller-analytics-api.wildberries.ru/api/v2/search-report/product/search-texts"

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
        return response.json()

class WildberriesBidderCPMWorker(WildberriesBidderWorkerMixin):
    def __init__(self, token: str, url: str, http_client: BaseHttpClient):
        super().__init__(url=URL_CPM, token=token, http_client=http_client)

    async def change_cpm(self, change_cpm: CPMChangeSchema) -> dict:
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=change_cpm)

class WildberriesBidderStatsWorker(WildberriesBidderWorkerMixin):
    def __init__(self, token: str, url: str, http_client: BaseHttpClient):
        super().__init__(url=URL_STAT, token=token, http_client=http_client)

    async def get_current_position_in_top(self, current_position_form: CurrentPositionSchema):
        return await self._send_request_and_get_json_from_response(method="post", data_to_request=current_position_form)