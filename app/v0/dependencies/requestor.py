import asyncio
import httpx

from .exceptions import CustomHTTPException
from .handle_exception import handle_requestor_exception
from core.settings import settings


class HttpxRequestor:

    @staticmethod
    async def send(url: str) -> list:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text.split(' ')
        except Exception as e:
            handle_requestor_exception(e)