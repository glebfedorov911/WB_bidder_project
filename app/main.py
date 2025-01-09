from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from v0 import router as router_v0
from core.settings import settings

import uvicorn


app = FastAPI()

app.include_router(router_v0, prefix=settings.api.prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)