from abc import ABC, abstractmethod

import httpx

from .exceptions import *


class BaseHttpClient(ABC):

    @abstractmethod
    async def send_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        ...

class HttpxHttpClient(BaseHttpClient):
    async def send_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            self.client = client
            return await self._request(method=method, url=url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            http_method = getattr(self.client, method)
            
            response = await http_method(url, **kwargs)
            return response
        except httpx.RequestError:
            raise ValueError(INVALID_REQUEST)
        except httpx.TimeoutException:
            raise ValueError(TIME_LIMIT_IS_REACHED)
        except httpx.HTTPStatusError as e:
            raise ValueError(STATUS_ERROR.format(status_code=e.response.status_code))
        except:
            raise ValueError(INTERNAL_SERVER_ERROR)