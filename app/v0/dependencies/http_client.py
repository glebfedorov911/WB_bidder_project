import asyncio
import httpx

from .exceptions import CustomHTTPException
from .handle_exception import handle_http_client_exception
from core.settings import settings


class HttpxHttpClient:

    @staticmethod
    async def send(url: str) -> list:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text.split(' ')
        except Exception as e:
            handle_http_client_exception(e)