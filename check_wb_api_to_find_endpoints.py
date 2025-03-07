import asyncio
import json

import httpx


API_KEY = """eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NzEyMzM2OSwiaWQiOiIwMTk1NzBkZS00MzA3LTdiOWMtODM4Yi1kMjIyYmQ2OGQwOGUiLCJpaWQiOjI5MzgxMTkzLCJvaWQiOjE4Mjk2NywicyI6MTI2LCJzaWQiOiJjZTYzZjU4YS05ODI3LTRiMzctOTQ1YS1iMTNlNWQ4NmZjZTUiLCJ0IjpmYWxzZSwidWlkIjoyOTM4MTE5M30.SlFB07pm17jIP7AumxQ4MqWA0o6ULrjE4uWN00Fm5b6AHebM_8pQw9TZ5RH-b5tjjT8Fp8Od3Gt2nIeo2E9R-A"""

HEADERS = {
    "Authorization": API_KEY
}

async def report():
    URL = "https://seller-analytics-api.wildberries.ru/api/v2/search-report/report"
    JSON = {
        "currentPeriod": {
            "start": "2025-03-07",
            "end": "2025-03-07"
        },
        "nmIds": [
            240664574
        ],
        "positionCluster": "all",
        "orderBy": {
            "field": "avgPosition",
            "mode": "asc" 
        },
        "limit": 100,
        "offset": 0
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            headers=HEADERS,
            url=URL,
            json=JSON
        )

        return response.json()

def sync_report():
    return asyncio.run(report())

report = sync_report()["data"]["groups"][0]["items"][0]["avgPosition"]
print("report", report)