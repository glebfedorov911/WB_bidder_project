import asyncio
import httpx

from .exceptions import CustomHTTPException
from core.settings import settings


class HttpxRequestor:

    @staticmethod
    async def send(url: str) -> list:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text.split(' ')
        except httpx.TimeoutException as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException("Request timeout")
        except httpx.HTTPStatusError as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException(f"Http code: {e.response.status_code}")
        except httpx.Request as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException(f"Error while request sending")
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException("Internal Server Error")