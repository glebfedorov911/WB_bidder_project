import asyncio
import httpx


class HttpxRequestor:

    @staticmethod
    def send(url: str) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text.split(' ')